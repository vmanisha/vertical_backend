# TODO (mverma): Remove repeated clicks for the same document
import argparse
import pandas as pd
import numpy as np
import json
import os
import re
from datetime import datetime
import urllib
# Query pattern to extract from server url.
query_id_pattern = 'queryid=(.*?)&'
query_id_regex = re.compile(query_id_pattern)

# Query pattern to extract from server url.
page_id_pattern = 'page=(.*?)&'
page_id_regex = re.compile(page_id_pattern)

# Query pattern to extract from server url.
docurl_pattern = 'docurl=(.*)'
docurl_regex = re.compile(docurl_pattern)

def FormatUrl(url):
    # Just remove the last char /
    if url[-1] == '/':
        url = url[: -1]
    '''
    if url.find('http://') == 0:
        url = url[7:]
    if url.find('https://') == 0:
        url = url[8:]
    '''
    print url
    url = url[url.find('.')+1:]
    print url
    return url

# Always on serp
def BreakEventUrl(url):
        url_split = url.split('&')
        query = None
        user = None
        task = None
        page = None
        if len(url_split) == 4:
            query = url_split[0][url_split[0].rfind('=')+1:].replace('+',' ')
            user =  url_split[1][url_split[1].rfind('=')+1:]  
            task =  url_split[2][url_split[2].rfind('=')+1:]  
            page =  url_split[3][url_split[3].rfind('=')+1:]  
	return user, task, page, query

# Some doc_url does not have queryid and pageid 
# (e.g., https://m.youtube.com/watch?v=RZ_YOAlPJNY)
# We use empty strings if we do not find any match
def BreakServerUrl(url):
	query_id = re.search(query_id_regex,url)
	if not query_id:
		query_id = -1
	else:
		query_id = query_id.group(1)

	page_id = re.search(page_id_regex, url)
	if not page_id:
		page_id = -1
	else:
		page_id = page_id.group(1)

	doc_url = re.search(docurl_regex,url)
	if not doc_url:
		doc_url = url
	else:
		doc_url = doc_url.group(1)

	return query_id, page_id, FormatUrl(doc_url)
'''
Convert an array of databases to a tsv. 
@databases can be an array of Json objects.
@columns is the column header to assign to pandas object.

'''
def FormatPageResponseDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
	    # Format of Page Response db
	    # "time_stamp":{"user_id":"marzipan","task_id":"8",
	    # "doc_url":"page=1&docid=aid_2&queryid=0&user=marzipan&task=8&docurl=url",
	    # "response_type":"relevance","response_value":"5.0"},
	    query_id, page_id, doc_url = BreakServerUrl(values['doc_url'])
            doc_url = FormatUrl(urllib.unquote(urllib.unquote(doc_url)))
	    new_entry = [entry , values['user_id'] , int(values['task_id']),\
		int(query_id), int(page_id), doc_url, values['response_type'], \
                values['response_value']]
	    tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
    return tsv_frame.drop_duplicates()

def FormatTaskResponseDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
            # Format of Task Response db
            # "time_stamp":{"user_id":"marzipan","task_id":"8",
            # "response_type":"preferred_verticals",
            # "response_value":"Images , Wiki , General Web"}
            new_entry = [entry , values['user_id'] , int(values['task_id']),\
            values['response_type'],values['response_value']]
            tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)
    return tsv_frame.drop_duplicates()

def FormatQueryResultDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
            # Format of Query Result db
            # "time_stamp":{"user_id":"","query_id":4,"task_id":"4","query_text":"","page_id":1,"search_results":[["i",[{"title":"","external_url":"","display_url":"","thumbnail":""},{"title":"","external_url":"","display_url":"","thumbnail":""}...]],["o",{"title":"","desc":"","display_url":"","external_url":""}],["o",{"title":"","desc":"","display_url":"","external_url":""}]...]}
            search_results = values['search_results']

            # The documents are stored in the order in which
            # they are displayed on the search results page.
            doc_pos = 0
            for result in search_results:
                doc_type = result[0]

                # All verticals have only one result except image
                # In case of image vertical we show multiple images
                # so pick the first image and ignore the rest
                if (doc_type == 'i'):
                    doc_prop = result[1][0]
                else:
                    doc_prop = result[1]

                doc_title = doc_prop['title']
                doc_url = FormatUrl(doc_prop['external_url'])
                new_entry = [entry , values['user_id'] , int(values['task_id']),\
                    int(values['query_id']), values['query_text'].strip(), int(values['page_id']), \
                    doc_pos, doc_type, doc_title, doc_url]
                tsv_data.append(new_entry)

                # Document position starts with zero
                doc_pos = doc_pos + 1
    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)
    return tsv_frame.drop_duplicates()

def FormatClickResultDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
            # Format of Click Result db
            #{"time_stamp":{"user_id":"marzipan","query_id":"0",
            #"page_id":"1","task_id":"8","doc_id":"aid_1",
            #"doc_url":"http://www.theplunge.com/bachelorparty/bachelor-party-ideas-2/"}
            new_entry = [entry , values['user_id'] , int(values['task_id']),\
                    int(values['query_id']),int(values['page_id']), \
                    values['doc_id'],FormatUrl(values['doc_url'])]
            tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    return tsv_frame.drop_duplicates()


def ProcessEventValueDict(event_value):
    # Contains html, prop and visible elements
    # Leave the html for now. 
    split = event_value['prop'].split(' ')
    return  int(split[9][split[9].rfind('_')+1:])

def FormatEventDB(databases, dbcolumns, sort_keys):
    tsv_data= []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
	    user, task, page, query = BreakEventUrl(values['doc_url'])
            if (query and user and task and page) and (values['event_type'] == 'tap'):
                element_tap = ProcessEventValueDict(values['event_value'])
                new_entry = [entry , user , int(task), query.strip(), int(page), \
                    values['event_type'], element_tap ]
                tsv_data.append(new_entry)
             
    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    return tsv_frame.drop_duplicates()

