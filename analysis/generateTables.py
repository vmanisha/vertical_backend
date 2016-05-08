import argparse
import pandas as pd
import numpy as np
import json
import re

# Construct several tables. 
#               Find the distribution of following variables:
#
#   a. task : users. Compute the number of users who provided task feedback
#   b. task : user_impressions. Compute the number of users who executed a
#    task.
#-----------------------------------------------------------------------------
#   c. task : vertical_views. Compute the number of times each vertical 
#       was shown as top result. 
#   d. task : queries. Compute the number of queries fired for the task.
#   e. task : clicks. Compute the number of clicks for the task. 
#   f. task : time . Compute the time spent on doing each task.
#   g. task : click_ranks. Compute the number of times a document was clicked
#   on a rank (remember to take page_number into account). 
#   h. task : time_to_first_click. Compute the time to first click for each
#   task. Compute mean and standard deviation. 
#   j. task : first_click_position. Compute the list of ranks that were clicked
#   first for task. 
#   k. task : last_click_position. Compute the ranks that were clicked last for
#   each task. 
#-----------------------------------------------------------------------------
#   h. task : vertical_queries. Compute the number of queries fired for the
#   task per vertical.
#   i. task : verticals_clicked. Compute the number of results that were clicked 
#   per vertical.
#   j. task : vertical_time. Compute the time doing task when a vertical was
#   top result. 
#   k. task : vertical_click_ranks. Compute the ranks that were clicked for
#   task given that vertical result was shown on top. 
#   l. task : time_to_click_veritcal. Compute the time to first click for each
#   task. Compute mean and standard deviation. 
#   m. task : first_click_position_vertical. Compute the list of ranks that were clicked
#   first for task for each vertical.  
#   n. task : last_click_position. Compute the ranks that were clicked last for
#   each task given a vertical was shown on top. 
#------------------------------------------------------------------------------


# Query pattern to extract from server url.
query_id_pattern = 'queryid=(.*?)&'
query_id_regex = re.compile(query_id_pattern)

# PageId pattern to extract from server url.
page_id_pattern = 'pageid=(.*?)&'
page_id_regex = re.compile(page_id_pattern)

# Docurl pattern to extract from server url.
docurl_pattern = 'docurl=(.*?)&'
docurl_regex = re.compile(docurl_pattern)

def ReadDB(event_file):
    event_db = json.load(event_file)
    return event_db

def BreakServerUrl(url):
	query_id = re.match(query_id_regex, url) 
	page_id = re.match(page_id_regex, url) 
	docurl_id = re.match(docurl_regex, url) 
	return query_id, page_id, docurl_id

'''
Convert an array of databases to a tsv. 
@databases can be an array of Json objects.
@columns is the column header to assign to pandas object.

'''
def FormatPageResponseDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
	    # Format of Page Response db
	    # "time_stamp":{"user_id":"marzipan","task_id":"8",
	    # "doc_url":"page=1&docid=aid_2&queryid=0&user=marzipan&task=8&docurl=url",
	    # "response_type":"relevance","response_value":"5.0"}
	    query_id, page_id, doc_url = BreakServerUrl(values['doc_url'])
	    new_entry = [entry , values['user_id'] , values['task_id'],\
			query_id, page_id, url,
                        values['response_type'], \
                        values['response_value']]
            tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)
    return tsv_frame 


def main():
    parser = argparse.ArgumentParser(description='Find and plot statistics\
            about vertical search related data.')
    parser.add_argument('-p','--pageResponseDB', help='Page response db from the\
            interface',required=True)
    parser.add_argument('-f','--isFolder', help='Indicate whether database\
    is in one file or files in one folder',action='store_true')

    arg = parser.parse_args()
    page_response_db = []
    # If a single event and response db file
    print arg.isFolder
    if not arg.isFolder:
        p_db = ReadDB(open(arg.pageResponseDB,'r'))
	page_response_db.append(p_db)

    else:
        for pfile in os.listdir(arg.pageResponseDB):
            p_db = ReadDB(open(arg.pageResponseDB+'/'+efile,'r'))
	    page_response_db.append(p_db)
            
    # Format page response db
    page_response_table = FormatPageResponseDB(page_response_db, ['time','user_id',\
			'task_id','query_id','page_id','url','response_type',\
			'response_value' ], ['time'])

