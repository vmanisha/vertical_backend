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
query_id_regex = re.compile('queryid=(.*?)&')

# Query pattern to extract from server url.
query_regex = re.compile('query=(.*?)(&|\Z)')

# Task pattern to extract from event url.
task_id_regex = re.compile('task=(.*?)&')

# user id to extract from event url.
user_id_regex = re.compile('user=(.*?)(&|\Z)')

# Query pattern to extract from server url.
page_id_regex = re.compile('page=(.*?)(&|\Z|#)')

# doc url pattern to extract from server url.
docurl_regex = re.compile('docurl=(.*)')

visibility_events = ['initial_state','panleft','panright','panup','pandown']
scroll_events = ['panleft','panright','panup','pandown', 'swipeleft','swiperight']

#TODO: Format URLs while loading all the db
#FIX: Format URLs removing some initial part of the url (e.g., wikipedia.org)
def FormatUrl(url):
    # Just remove the last char / and #
    url = urllib.unquote(urllib.unquote(url))
    if url[-1] == '/' or url[-1] == '#':
        url = url[: -1]
    if url.find('http://') == 0:
        url = url[7:]
    if url.find('https://') == 0:
        url = url[8:]
    if url.find('www.') == 0:
        url = url[4:]
    if url.find('en.m.') == 0:
        url = url[5:]
    if url.find('en.') == 0:
        url = url[3:]
    if url.find('m.') == 0:
        url = url[2:]
    url = url.strip()
    # Fix ebay errors
    url = url.replace(' ','+')
    return url

def GetValueFromRegex(regex, string, default):
  variable = re.search(regex,string)
  value = None
  if not variable:
    value = default
  else:
    value = variable.group(1)
  return value
  
# Always on serp
# TODO: Should we call FormatUrl here as well?
def BreakEventUrl(url):
  query = GetValueFromRegex(query_regex, url,'').replace('+',' ')
  user = GetValueFromRegex(user_id_regex, url,'')
  task = GetValueFromRegex(task_id_regex, url,-1)
  page = GetValueFromRegex(page_id_regex, url,-1)
  return user, task, page, query

# Some doc_url does not have queryid and pageid
# (e.g., https://m.youtube.com/watch?v=RZ_YOAlPJNY)
# We use empty strings if we do not find any match
def BreakServerUrl(url):
  query_id = GetValueFromRegex(query_id_regex,url, -1)
  page_id = GetValueFromRegex(page_id_regex, url, -1)
  doc_url = GetValueFromRegex(docurl_regex,url, url)
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
	    if doc_url:
	    	doc_url = FormatUrl(doc_url)
	    new_entry = [entry , values['user_id'] , int(values['task_id']),\
		int(query_id), int(page_id), doc_url, values['response_type'], \
                float(values['response_value'])]
	    tsv_data.append(new_entry)

    # create a new data frame
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

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

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
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
                # so concatenate all the images into one url. 
                if (doc_type == 'i'):
                    doc_url = ''
                    for image in result[1]:
                        doc_url += ' '+FormatUrl(image['external_url'])
                else:
                    doc_url = FormatUrl(result[1]['external_url'])
                new_entry = [entry , values['user_id'] , int(values['task_id']),\
                    int(values['query_id']), values['query_text'].strip(), int(values['page_id']), \
                    doc_pos, doc_type, doc_url]
                tsv_data.append(new_entry)

                # Document position starts with zero
                doc_pos = doc_pos + 1
    # create a new data frame
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
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
            if not FormatUrl(values['doc_url']):
                print values['doc_url'], FormatUrl(values['doc_url'])
            new_entry = [entry , values['user_id'] , int(values['task_id']),\
                    int(values['query_id']),int(values['page_id']), \
                    values['doc_id'],FormatUrl(values['doc_url'])]
            tsv_data.append(new_entry)

    # create a new data frame
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
    return tsv_frame.drop_duplicates()

# @prop: timestamp+" "+deltaTime+" "+deltaX+" "+deltaY+" "+
# velocityX+" "+velocityY+" "+direction+" "+distance+" "+newtag+" "+height;
def ProcessPropInEvents(prop_string):
  hammer_direction = {'2':'left', '4':'right', '8':'up', '16':'down',
        '6':'horizontal','24':'vertical','30':'all','1':'none'}
  prop_dict = {}
  val_string = ' '.join(prop_string.split())
  split = val_string.split(' ')
  prop_dict['delta_time'] = float(split[1])
  try:
    prop_dict['win_height'] = float(split[-1])
  except:
    prop_dict['win_height'] = -1
  prop_dict['vel_x'] = float(split[4])
  prop_dict['vel_y'] = float(split[5])
  prop_dict['delta_x'] = float(split[2])
  prop_dict['delta_y'] = float(split[3])
  try :
      prop_dict['element'] = int(split[8][split[8].rfind('_')+1:])
  except:
      prop_dict['element'] = -1
  prop_dict['distance'] = float(split[7])
  prop_dict['direction'] = hammer_direction[split[6]]
  return prop_dict

'''
Event dict has different format for different events.
The format for different event types is given below:
  Tap or double tap: ,"event_type":"tap","event_value":{"html":"Bachelor",
  "prop":" 1462459928613 83 0 0 0 0 1 0 aid_0  1996"}}
  pan and swipe: "event_type":"panup","event_value":{"html":"A wild",
  "prop":" 1462459948379 466 41 -103 0 0 8 111 bott_id_1 card_bottom  1996",
  "visible_elements":"card_id_1"}}
  initial_state: "event_type":"initial_state","
  event_value":{"visible_elements":"card_id_0"}}
'''
def FormatAllEventDB(databases, dbcolumns, sort_keys):
  # Store all events in a table. Mainly for markov transition calculation.
  # Format is : event_type, event_element, visible_elements, distance,
  # direction, win height, delta_x , delta_y.
  # keep nothing where events are taps. 
  tsv_data = []
  for database in databases:
    for entry, values in database.items():
        entry = datetime.fromtimestamp(float(entry)/1000)
        user, task, page, query = BreakEventUrl(values['doc_url'])
        if not page:
          page = -1
        new_entry = [entry , user , int(task), query.strip(), int(page),\
                    values['event_type']]
        event_dict = values['event_value']

        if 'prop' in event_dict:
          prop_dict = ProcessPropInEvents(event_dict['prop'])
          new_entry.append(prop_dict['element'])
          new_entry.append(prop_dict['direction'])
          new_entry.append(prop_dict['delta_time'])
        else:
          new_entry.append(-1)
          new_entry.append('')
        if 'visible_elements' in event_dict:
          new_entry.append(event_dict['visible_elements'])
        else:
          new_entry.append("")
        tsv_data.append(new_entry)
  # create a new data frame
  tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

  # Remove test users
  tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

  # sort by time key
  tsv_frame = tsv_frame.sort(sort_keys)

  # Remove duplicate rows
  return tsv_frame.drop_duplicates()
        

def FormatEventDBForTap(databases, dbcolumns, sort_keys):
    tsv_data= []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
            user, task, page, query = BreakEventUrl(values['doc_url'])
            if (query and user and task and page) and (values['event_type'] == 'tap'):
                prop_dict = ProcessPropInEvents(values['event_value'])
                if prop_dict['element'] > -1:
                    new_entry = [entry , user , int(task), query.strip(), int(page), \
                    values['event_type'], prop_dict['element']  ]
                    tsv_data.append(new_entry)

    # create a new data frame
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
    return tsv_frame.drop_duplicates()

def FormatEventDBForScrolls(databases, dbcolumns, sort_keys):
    tsv_data= []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
            user, task, page, query = BreakEventUrl(FormatUrl(values['doc_url']))
            # Track visibility only on first page and for events listed in visibility_events
            if (query and user and task) and (int(page) == 1) and\
            (values['event_type'] in scroll_events):
                event_value = values['event_value']
                # Only consider entries that have visible_elements
                if 'prop' in event_value:
                    # Get the window height, distance, and element and visible
                    # elements. 
                    prop_dict = ProcessPropInEvents(event_value['prop'])
                    visible = ''
                    if 'visible_elements' in event_value:
                        visible = event_value['visible_elements']
                    new_entry = [entry , user , int(task), query.strip(), \
                        values['event_type'], prop_dict['element'], visible,\
                        prop_dict['distance'],prop_dict['direction'],\
                        prop_dict['win_height'], prop_dict['vel_x'],
                        prop_dict['vel_y']]
                    tsv_data.append(new_entry)
    # create a new data frame
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
    return tsv_frame.drop_duplicates()


def FormatEventDBForVisibility(databases, dbcolumns, sort_keys):
    tsv_data= []
    for database in databases:
        for entry , values in database.items():
            entry = datetime.fromtimestamp(float(entry)/1000)
            user, task, page, query = BreakEventUrl(FormatUrl(values['doc_url']))
            # Track visibility only on first page and for events listed in visibility_events
            if (query and user and task) and (int(page) == 1) and (values['event_type'] in visibility_events):
                event_value = values['event_value']
                # Only consider entries that have visible_elements
                if 'visible_elements' in event_value:
                    new_entry = [entry , user , int(task), query.strip(), \
                        values['event_type'], event_value['visible_elements']]
                    tsv_data.append(new_entry)

    # create a new data frame
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)

    # Remove test users
    tsv_frame = tsv_frame[~tsv_frame['user_id'].str.contains('test')]

    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
    return tsv_frame.drop_duplicates()

