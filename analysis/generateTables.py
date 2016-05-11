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
#   b. task : user_impressions. Compute the number of users who executed a
#    task.
#-----------------------------------------------------------------------------
#   c. task : vertical_views. Compute the number of times each vertical 
#       was shown as top result. 
#   d. task : queries. Compute the number of queries fired for the task.
#   e. task : clicks. Compute the number of clicks for the task. 
#   f. task : time . Compute the time spent on doing each task.
#   g. task : click_ranks. Compute the number of times a position was clicked
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

TASKMAP = {'Somewhat Satisfied': 2.0, 'Highly Satisfied': 3.0, 'Not Satisfied' : 1.0}

def FindTimeToFirstClick(click_table, result_table):

    # Find the first-result type for each tuple (query_id, task_id, user_id,
    # page_id)
    first_result_type =  result_table[result_table['doc_pos'] == 0]
    first_result_type = first_result_type[['query_id','user_id','task_id',\
            'page_id', 'doc_pos','doc_type']]

    # Merge click and results. Will filter clicks whose origin was not serp. 
    result_table['doc_url'] = result_table['doc_url'].str.strip();
    click_table['doc_url'] = click_table['doc_url'].str.strip();

    merged_result_and_click = pd.merge(result_table[['time','user_id','task_id',\
            'query_id','page_id', 'doc_url','doc_pos','doc_type',]],click_table, \
            left_on = ['user_id','task_id','query_id','page_id', 'doc_url'], \
            right_on =['user_id','task_id','query_id','page_id', 'doc_url'])

    # Take the time difference of times.  
    merged_result_and_click['time_x'] =  pd.to_datetime(merged_result_and_click['time_x'],unit='s')
    merged_result_and_click['time_y'] =  pd.to_datetime(merged_result_and_click['time_y'],unit='s')

    merged_result_and_click['time_diff']= merged_result_and_click['time_y']-\
            merged_result_and_click['time_x']

    # Drop the times 
    merged_result_and_click = merged_result_and_click.drop(['time_x'], axis = 1)

    # Take the intersection.
    all_clicks_with_result_type = pd.merge(merged_result_and_click,\
            first_result_type, left_on = ['user_id','task_id','query_id',\
            'page_id'], right_on = ['user_id','task_id','query_id',\
            'page_id'])

    # sort by time, task-id, user-id and query-id
    all_clicks_with_result_type = all_clicks_with_result_type.sort(\
            ['time_y','user_id','task_id','query_id']);
    all_clicks_with_result_type.to_csv('all_clicks_with_result_type.csv',
            encoding = 'utf-8', sep = '\t', index = False)

    # Just select the first and last entry for each combination (task_id,
    # query_id, user_id, and page_id)

def FindDescriptiveStatsPerVertical(result_table, click_table, page_table,\
        task_table):
    # Find the following stats per vertical: 
    # Image Video Wiki : sess, queries, clicks, page-response and
    # task-responses.

    result_table['type'] = 'results'
    click_table['type'] = 'click'
    page_table['type'] = 'page_response'
    task_table['type'] = 'task_response'
    user_stats = {}
    vertical_stats = {
            'i' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel':[],\
                'page_sat':[], 'task_sat':[]}, \
            'v' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel': [],\
                'page_sat':[], 'task_sat':[]}, \
            'o' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel':[],\
                'page_sat':[], 'task_sat':[]}, \
            'w' :  {'sess':0.0, 'query': [], 'clicks':[],'page_sat':[],\
                'page_rel':[],'task_sat':[]}
    }
    
    # Concatinate all tables. Keep only the first result. 
    # values not present will be N/A
    result_first = result_table[result_table['doc_pos'] == 0]
    concat_table = pd.concat([result_first, click_table, page_table,\
        task_table], ignore_index = True)
   
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
            round(np.std(stat_dict['task_sat']),2)




def LoadDatabase(filename, isFolder):
    database = []

    if not isFolder:
        db = json.load(open(filename,'r'))
        database.append(p_db)

    else:
        for ifile in os.listdir(filename):
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
    parser.add_argument('-f','--isFolder', help='Indicate whether database\
    is in one file or files in one folder',action='store_true')

    arg = parser.parse_args()
    page_response_db =  LoadDatabase(arg.pageResponseDB, arg.isFolder)
    task_response_db = LoadDatabase(arg.taskResponseDB,arg.isFolder)
    query_result_db = LoadDatabase(arg.queryResultDB,arg.isFolder)
    click_result_db = LoadDatabase(arg.clickResultDB,arg.isFolder)

    # Format page response db
    page_response_table = FormatPageResponseDB(page_response_db, page_response_header, page_reponse_sortkeys)
    
    # Format task response db
    task_response_table = FormatTaskResponseDB(task_response_db,task_response_header,task_response_sortkeys)

    # Format query result db
    query_table = FormatQueryResultDB(query_result_db,query_result_header,query_result_sortkeys)
    
    # Format click result db
    click_table = FormatClickResultDB(click_result_db,click_result_header,click_result_sortkeys)

    # Remove test users
    page_response_table = page_response_table[~page_response_table['user_id'].str.contains('test')]
    task_response_table = task_response_table[~task_response_table['user_id'].str.contains('test')]
    query_table = query_table[~query_table['user_id'].str.contains('test')]
    click_table = click_table[~click_table['user_id'].str.contains('test')]

    # a. task : users. Compute the number of users who provided task feedback
    # task_id, #users_who_gave_feedback
    task_response_table[['task_id','user_id']].groupby(['task_id']).\
            agg({'user_id': pd.Series.nunique}).to_csv('task_feedback.csv')

    # b. task : user_impressions. Compute the number of users who executed a task.
    # task_id, #users_who_executed_task
    page_response_table[['task_id','user_id']].groupby(['task_id']).\
            agg({'user_id': pd.Series.nunique}).to_csv('task_execute.csv')

    # c. task : vertical_views. Compute the number of times each vertical was shown as top result. 
    # Only consider query results in the first page (page_id==1)
    # Here we output counts for all the doc position in the first page
    # task_id, doc_type, doc_pos, #occurances
    query_results = query_table[(query_table['page_id']==1) & \
            (query_table['doc_pos'] == 0)]
    query_results[['task_id','doc_type']].groupby(\
            ['task_id','doc_type']).\
            count().to_csv('vertical_pos.csv')

    # d. task : queries. Compute the number of queries fired for the task.
    # task_id, #unique_queries
    queries_with_time= query_table[\
            ['time','task_id','query_text']].drop_duplicates();
    
    queries_with_time.groupby(['task_id','query_text']).agg(\
            {'query_text': pd.Series.count}).to_csv('task_queries.csv')

    # e. task : clicks. Compute the number of clicks for the task. 
    # task_id, click_url, #clicks
    click_table[['task_id','doc_url']].groupby(['task_id','doc_url']).\
            count().to_csv('task_clicks.csv',encoding='utf-8',sep='\t')

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

    FindTimeToFirstClick(click_table, query_table);
    FindDescriptiveStatsPerVertical(query_table, click_table,\
            page_response_table, task_response_table)


    

    # h. task : time_to_first_click. Compute the time to first click for each
    # task. Compute mean and standard deviation. 
    # Replace multiple columns with one. 
    
    # j. task : first_click_position. Compute the list of ranks that were clicked first for task. 
    # task_id, doc_pos, #first_clicks

    # k. task : last_click_position. Compute the ranks that were clicked last for
    # each task. 
    # task_id, doc_pos, #last_clicks

if __name__ == "__main__":
    main()
