import argparse
import pandas as pd
import numpy as np
import json
import os
import re
from datetime import datetime
from formatTables import *

# Construct several tables. 
#               Find the distribution of following variables:
#
#   a. task : users. Compute the number of users who provided task feedback
#   b. task : user_impressions. Compute the number of users who executed task.
#-----------------------------------------------------------------------------
#   c. vertical_type : vertical_views. Compute the number of times each vertical 
#       was shown as top result. 
#   d. vertical_type : queries. Compute the number of queries fired for the vertical_type.
#   e. vertical_type : clicks. Compute the number of clicks for the vertical_type. 
#   f. vertical_type : time . Compute the time spent on doing each vertical_type.
#   g. vertical_type : click_ranks. Compute the number of times a position was clicked
#   on a rank (remember to take page_number into account). 
#   h. vertical_type : time_to_first_click. Compute the time to first click for each
#   vertical_type. Compute mean and standard deviation. 
#   j. vertical_type : first_click_position. Compute the list of ranks that were clicked
#   first for vertical_type. 
#   k. vertical_type : last_click_position. Compute the ranks that were clicked last for
#   each vertical_type. 
#------------------------------------------------------------------------------

# Page response table header
page_response_header = ['time','user_id','task_id','query_id','page_id',\
	'doc_url','response_type','response_value']
# Page response table sortkeys
page_reponse_sortkeys = ['time','task_id','query_id']

# Task response table header
task_response_header = ['time','user_id','task_id','response_type','response_value']
# Task response table sortkeys
task_response_sortkeys = ['time','task_id']

# Query result table header
query_result_header = ['time','user_id','task_id','query_id','query_text','page_id','doc_pos','doc_type','doc_title','doc_url']
# Query result table sortkeys
query_result_sortkeys = ['time','task_id','query_text','doc_pos']

# Click result table header
click_result_header = ['time','user_id','task_id','query_id','page_id','doc_id','doc_url']
# Click result table sortkeys
click_result_sortkeys = ['time','task_id']

# Event table header
event_header = ['time','user_id','task_id','query_text','page_id','event_type','event_value']
# Task response table sortkeys
event_sortkeys = ['time','task_id', 'user_id']

TASKMAP = {'Somewhat Satisfied': 2.0, 'Highly Satisfied': 3.0, 'Not Satisfied' : 1.0}


def MergeAllTables(result_table, click_table, event_table, page_table, task_table):
    result_table['type'] = 'results'
    click_table['type'] = 'click'
    page_table['type'] = 'page_response'
    task_table['type'] = 'task_response'
    event_table['type'] = 'event_response'
    
    # Concatinate all tables. Keep only the first result. 
    # values not present will be N/A
    # result_first = result_table[result_table['doc_pos'] == 0]
    concat_table = pd.concat([result_first, click_table,event_table, page_table,\
        task_table], ignore_index = True)
    concat_table = concat_table.drop(['doc_title'], axis = 1)
    return concat_table


def FindFirstAndLastClickInfo(concat_table):
    # Groupby task_id, user_id. 
    # For each result type:
    # Record time to first click
    # Record time to last click 
    # (Image and video clicks would not have been recorded !) 
    # Can we use page response proxy?
    user_stats = {}
    not_registered_clicks = 0.0
    vertical_stats = {
            'i' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[] }, \
            'v' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[] }, \
            'w' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[]  }, \
            'o' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[]  }, \
    }
    
    # Remove task responses.
    concat_table = concat_table[~concat_table['type'] == 'task_response']
    #concat_table = concat_table.drop(['doc_title','doc_pos'], axis = 1)
    
    # Group by task_id and query_id and Sort by time within each group. 
    grouped_table = concat_table.sort(['time']).groupby(['task_id','user_id'])
    for name, group in grouped_table:
		vert_type = None
		first_click = None
		first_time = None
		last_time = None
		last_click = None
		result_time = None
		rows = []
		results = {}
		for index, row in group.iterrows():
            rows.append(row)
		
		for i in range(len(rows)):
			row = rows[i]
			# Store results.
			if row['type'] == 'results':
				results[row['doc_pos']] = row

			if row['type'] == 'results' and row['doc_pos'] == 0:
				# check prev result data. 
				if vert_type and first_click and last_click:
					vertical_stats[vert_type]['first_rank'].append(first_click)
					vertical_stats[vert_type]['last_rank'].append(last_click)
					vertical_stats[vert_type]['first_click'].append(first_time)
					vertical_stats[vert_type]['last_click'].append(last_time)
					# Set everything to null.
					first_click = None
					first_time = None
					last_time = None
					last_click = None
					result_time = None
					vert_type = None
				# Set vertical type for this page and request time. 
				vert_type = str(row['doc_type']).strip()
				result_time = row['time']

			# Found a tap or a click 
			start_time  = row['time']
			etype = None
			click_rank = None
			found = False
			if (row['type'] == 'event_response'):
				click_url = results[row['event_value']]['doc_url']
				click_rank = int(row['event_value'])
				etype = 'tap'
				# Check if page response for this url has been submitted. 
				j = i+1
				while (rows[j]['type'] != 'results') and j < len(rows):
					if rows[j]['type'] == 'page_response' and \
							rows[j]['doc_url'] == click_url:
								found = True
								break
					else:
					   print tap_url, rows[j]['doc_url'], 'dont match'
					j+=1
			else:
				click_rank = int(row['doc_id'][row['doc_id'].find('_')+1:])
				etype = 'click'

			# Found the page score or click
			if  etype == 'click' or (etype == 'tap' and found):
				if click_rank > 0:
					vertical_stats[vert_type]['total_clicks']+=1.0
					vertical_stats[vert_type]['off_vert_click']+=1.0
					vertical_stats[vert_type]['off_vert_rank'].append(click_rank)

				if not first_click:
					first_click = click_rank
					first_time  = result_time - start_time
				last_click = click_rank
				last_time = result_time - start_time


def FindDescriptiveStatsPerVertical(concat_table):
    # Find the following stats per vertical: 
    # Image Video Wiki : sess, queries, clicks, page-response and
    # task-responses.
    user_stats = {}
    not_registered_clicks = 0.0
    vertical_stats = {
            'i' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel':[],\
                'page_sat':[], 'task_sat':[] , 'time' : [] }, \
            'v' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel': [],\
                'page_sat':[], 'task_sat':[], 'time': []}, \
            'o' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel':[],\
                'page_sat':[], 'task_sat':[], 'time': []}, \
            'w' :  {'sess':0.0, 'query': [], 'clicks':[],'page_sat':[],\
                'page_rel':[],'task_sat':[], 'time': []}
    }
    
    # Group by task_id and query_id and Sort by time within each group. 
    grouped_table = concat_table.sort(['time']).groupby(['task_id','user_id'])
    for name, group in grouped_table:
        user = name[1]
        task = name[0]
        if user not in user_stats:
            user_stats[user] = []
        if task not in user_stats[user]:
            user_stats[user].append(task)

        last_time = None
        sess = 0.0
        queries = 0.0
        clicks = {}
        page_sat = {}
        page_rel = {}
        task_sat = []
        time = []
        doc_type = None
        n_task_response = 0.0

        for index, row in group.iterrows():
            if row['type'] == 'results':
                if last_time == None:
                    # First query for task
                    last_time = row['time']
                    # Increment sessions.
                    sess+=1.0
                    doc_type = str(row['doc_type']).strip()
                # Record queries. 
                queries +=1.0
            
            if row['type'] == 'click':
                # Record only one click per url. 
                clicks[row['doc_url']] = 1.0

            # Not serp. 
            if (row['type'] == 'page_response') and ('128.16.12.66' not in\
                    row['doc_url']):
                if row['response_type'] == 'relevance':
                    # Record only last relevance label. 
                    page_rel[row['doc_url']] = float(row['response_value'])
                    
                    if row['doc_url'] not in clicks:
                        not_registered_clicks+=1.0
 
                    # Record only one click per url.
                    clicks[row['doc_url']] = 1.0
                
                if row['response_type'] == 'satisfaction':
                    page_sat[row['doc_url']] = float(row['response_value'])
            
            # Add to database 
            if (row['type'] == 'task_response') and (row['response_type'] ==\
                    'satisfaction'):
                if doc_type:
                    if n_task_response > 0:
                        print 'ERROR :',user, 'did task more than once?', task
                    vertical_stats[doc_type]['sess'] += sess
                    vertical_stats[doc_type]['query'].append(queries)
                    vertical_stats[doc_type]['clicks'].append(sum(clicks.values()))
                    vertical_stats[doc_type]['page_sat'].extend(page_sat.values())
                    vertical_stats[doc_type]['page_rel'].extend(page_rel.values())
                    vertical_stats[doc_type]['task_sat'].append(TASKMAP[row['response_value']])
                    task_time = (row['time'] - last_time).total_seconds()
                    if task_time < 2000:
                        vertical_stats[doc_type]['time'].append((row['time']-last_time).total_seconds())
                    else:
                        print task, user, task_time, 'Unusual time'
                else:
                    print 'There was no search in the beginning!', task,user,\
                    index
                n_task_response+=1.0
   
    # Count mean and std-dev of page responses and task responses.
    for vertical_type, stat_dict in vertical_stats.items():
        print vertical_type , stat_dict['sess'], np.mean(stat_dict['query']),\
            round(np.std(stat_dict['query']),2), np.mean(stat_dict['clicks']),\
            round(np.std(stat_dict['clicks']),2),np.mean(stat_dict['page_rel']),\
            round(np.std(stat_dict['page_rel']),2),np.mean(stat_dict['page_sat']),\
            round(np.std(stat_dict['page_sat']),2),np.mean(stat_dict['task_sat']),\
            round(np.std(stat_dict['task_sat']),2), np.mean(stat_dict['time']),\
            round(np.std(stat_dict['time']),2)
    print 'Not registered clicks ', not_registered_clicks

def LoadDatabase(filename, isFolder):
    database = []

    if not isFolder:
        db = json.load(open(filename,'r'))
        database.append(p_db)

    else:
        for ifile in os.listdir(filename):
            print ifile
            db = json.load(open(filename+'/'+ifile,'r'))
            database.append(db)
        
    return database


def main():
    parser = argparse.ArgumentParser(description='Find and plot statistics\
            about vertical search related data.')
    parser.add_argument('-p','--pageResponseDB', help='Page response db from the\
            interface',required=True)
    parser.add_argument('-t','--taskResponseDB', help='Task response db from the\
            interface',required=True)
    parser.add_argument('-q','--queryResultDB', help='Query result db from the\
            interface',required=True)
    parser.add_argument('-c','--clickResultDB', help='Click result db from the\
            interface',required=True)
    parser.add_argument('-e','--eventDB', help='Event db from the\
            interface',required=True)
    parser.add_argument('-f','--isFolder', help='Indicate whether database\
    is in one file or files in one folder',action='store_true')

    arg = parser.parse_args()
    page_response_db =  LoadDatabase(arg.pageResponseDB, arg.isFolder)
    task_response_db = LoadDatabase(arg.taskResponseDB,arg.isFolder)
    query_result_db = LoadDatabase(arg.queryResultDB,arg.isFolder)
    click_result_db = LoadDatabase(arg.clickResultDB,arg.isFolder)
    event_db = LoadDatabase(arg.eventDB,arg.isFolder)

    # Format page response db
    page_response_table = FormatPageResponseDB(page_response_db, page_response_header, page_reponse_sortkeys)
    
    # Format task response db
    task_response_table = FormatTaskResponseDB(task_response_db,task_response_header,task_response_sortkeys)

    # Format query result db
    query_table = FormatQueryResultDB(query_result_db,query_result_header,query_result_sortkeys)
    
    # Format click result db
    click_table = FormatClickResultDB(click_result_db,click_result_header,click_result_sortkeys)

    # Format click result db
    event_table = FormatEventDB(event_db,event_header, event_sortkeys)
    
    # Remove test users
    page_response_table = page_response_table[~page_response_table['user_id'].str.contains('test')]
    task_response_table = task_response_table[~task_response_table['user_id'].str.contains('test')]
    query_table = query_table[~query_table['user_id'].str.contains('test')]
    click_table = click_table[~click_table['user_id'].str.contains('test')]
    event_table = event_table[~event_table['user_id'].str.contains('test')]

    # a. task : users. Compute the number of users who provided task feedback
    # task_id, #users_who_gave_feedback
    task_response_table[['task_id','user_id']].groupby(['task_id']).\
            agg({'user_id': pd.Series.nunique}).to_csv('task_feedback.csv')

    # b. task : user_impressions. Compute the number of users who executed a task.
    # task_id, #users_who_executed_task
    page_response_table[['task_id','user_id']].groupby(['task_id']).\
            agg({'user_id': pd.Series.nunique}).to_csv('task_execute.csv')

    # c. vertical_type : vertical_SERPs. Compute the number of times each vertical was shown as top result. 
    # Only consider query results in the first page (page_id==1)
    # Here we output counts for all the doc position in the first page
    # doc_type, #occurances
    query_results = query_table[(query_table['page_id']==1) & \
            (query_table['doc_pos'] == 0)]
    print query_results.groupby(['doc_type'])['task_id'].count()

    # d. vertical_type : queries. Compute the number of queries fired for each vertical.
    # task_id, #unique_queries
    queries_with_time= query_results[['time','doc_type','query_text']].drop_duplicates();
    queries_with_time.groupby(['doc_type','query_text']).agg(\
            {'query_text': pd.Series.count}).to_csv('vert_queries.csv')

    # f. task : time . Compute the time spent on doing each task.

    # g. task : click_ranks. Compute the number of times a position was clicked
    # ignore positions with double digits as they are nested clicks
    # doc_pos = (page_id - 1) * 10 + doc_id
    # task_id, doc_pos, #clicks
    click_filtered = click_table[click_table['doc_id'].str.len()\
            == 5]
    click_filtered['doc_pos'] = (click_filtered['page_id'].astype(float) -\
            1.0) + (click_filtered['doc_id'].str[4]).astype(float)    
    # Filter the columns for count.
    click_filtered[['task_id','doc_pos']].groupby(['task_id','doc_pos'])['doc_pos'].\
            count().to_csv('task_rank_click_counts.csv', encoding = 'utf-8',\
            sep = '\t')

    click_filtered = click_table[click_table['doc_id'].str.len()\
            == 5]
    merged_tables = MergeAllTables(query_table, click_filtered, event_table, page_response_table, task_response_table)
    
    # Find the vertical_type stats: sessions, queries, clicks a
    # nd average satisfaction/rel values. 
    FindDescriptiveStatsPerVertical(merged_tables)

    # h. vertical_type : time_to_first_click. Compute the time to first click for each
    # j. vertical_type : first_click_position. Compute the list of ranks that were clicked first for task. 
    # k. vertical_type : last_click_position. Compute the ranks that were clicked last for
    


if __name__ == "__main__":
    main()
