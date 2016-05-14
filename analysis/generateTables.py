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
query_result_header =['time','user_id','task_id','query_id','query_text','page_id','doc_pos','doc_type','doc_url']
# Query result table sortkeys
query_result_sortkeys = ['time','task_id','query_text','doc_pos']

# Click result table header
click_result_header = ['time','user_id','task_id','query_id','page_id','doc_id','doc_url']
# Click result table sortkeys
click_result_sortkeys = ['time','task_id']

# tap event table header
tap_event_header = ['time','user_id','task_id','query_text','page_id','event_type','event_value']
# Tap event sortkeys
tap_event_sortkeys = ['time','task_id', 'user_id']

# Visibility event table header
vis_event_header = ['time','user_id','task_id','query_text','event_type','event_value']
# Visibility event table sortkeys
vis_event_sortkeys = ['time','task_id', 'user_id']

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
    concat_table = pd.concat([result_table, click_table,event_table, page_table,\
        task_table], ignore_index = True)
    concat_table.to_csv('concat_tables.csv', index = False, encoding = 'utf-8')
    return concat_table


def FindFirstAndLastClickInfo(concat_table):
    # For each result type: Record time to first click, Record time to last click
    # (Image and video clicks would not have been recorded ! Use taps. 

    vertical_stats = {
            'i' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[], 'on_vert_click':0.0 }, \
            'v' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[],'on_vert_click':0.0 }, \
            'w' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[], 'on_vert_click':0.0  }, \
            'o' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[] , 'on_vert_click':0.0 }, \
    }

    # Remove task responses.
    concat_table = concat_table[~concat_table['type'].str.contains('task_response')]

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
        recorded_clicks = {}
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
                    recorded_clicks = {}
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
                # check if in clicks.
                if click_url not in recorded_clicks:
	    	    click_rank = int(row['event_value'])+1
	    	    etype = 'tap'
	    	    # Check if page response for this url has been submitted.
	    	    j = i+1
	    	    while j < len(rows) and (rows[j]['type'] != 'results') :
	    	        if rows[j]['type'] == 'page_response' and \
	    	            (rows[j]['doc_url'] in click_url):
	    	        	found = True
                                recorded_clicks[click_url] = 1.0
	    	                break
	    	        j+=1
            if (row['type'] == 'click') and (row['doc_url'] not in\
                    recorded_clicks):
                # check if in taps. 
	    	click_rank = int(row['doc_id'][row['doc_id'].find('_')+1:])+1
	    	etype = 'click'
                recorded_clicks[row['doc_url']] = 1.0

	    # Found the page score or click
	    if  etype == 'click' or (etype == 'tap' and found):
	    	if click_rank > 0:
	            vertical_stats[vert_type]['total_clicks']+=1.0
                    if click_rank > 1:
	                vertical_stats[vert_type]['off_vert_click']+=1.0
	                vertical_stats[vert_type]['off_vert_rank'].append(click_rank)
                    else:
	                vertical_stats[vert_type]['on_vert_click']+=1.0

	    	if not first_click:
	            first_time  = (start_time - result_time).total_seconds()
                    if (first_time < 50):
	                first_click = click_rank
	    	last_click = click_rank
	    	last_time = (start_time - result_time ).total_seconds()
                # Set everything to null
                etype = None
                found = False

    for vertical_type, stats in vertical_stats.items():
        print vertical_type, stats['total_clicks'],\
        'off-click',stats['off_vert_click']/stats['total_clicks'],\
        'on-click',stats['on_vert_click']/stats['total_clicks'],\
        'off-rank',np.mean(stats['off_vert_rank']),np.std(stats['off_vert_rank']),\
        'first-rank',np.mean(stats['first_rank']),np.std(stats['first_rank']),\
        'last-rank',np.mean(stats['last_rank']),np.std(stats['last_rank']),\
        'first-time',np.mean(stats['first_click']),np.std(stats['first_click']),\
        'last-time',np.mean(stats['last_click']),np.std(stats['last_click'])
        

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


def IsSerpPage(url):
    return url.find('128.16.12.66:4730') > -1

def FindPageMetricsPerVertical(result_table, page_table):

    # Concat result and page tables
    result_table['type'] = 'results'
    page_table['type'] = 'page_response'
    concat_table = pd.concat([result_table, page_table], ignore_index = True)
    concat_table.to_csv('concat_result_page',encoding='utf-8', index = False)

    # Group by user_id and task_id and sort by time within each group
    grouped_table = concat_table.sort(['time']).groupby(['user_id','task_id'])
    # Set vertical type for each serp. 
    vert_type = None
    concat_table['first_result_type'] = ''

    # Iterate over all users and tasks
    for name, group in grouped_table:

        # Iterate over all page response results
        # for a specific user and a task
        for pindex, prow in group.iterrows():

            if prow['type'] == 'results' and prow['doc_pos'] == 0:
                vert_type = prow['doc_type']
            # Skip if the row is not a page_response
            # Skip if its an invalid page
            # serp pages are invalid pages
            # because no doc_pos for serp
            if prow['type'] != 'page_response' or IsSerpPage(prow['doc_url']):
                continue

            ptime = prow['time']
            purl = prow['doc_url']
            ppos = -1

            # Find the doc_pos from result entry
            for rindex, rrow in group.iterrows():

                # Get the doc_pos from the result entry
                # whose url matches with the page response url
                if rrow['type'] == 'results' and (purl in rrow['doc_url']):
                    ppos = rrow['doc_pos']

                # Search only those result entries which
                # has timestamp lower than the page response time
                if rrow['time'] > ptime:
                    break

            # if ppos = -1 that means we did not find the match
            # TODO: handle ppos=-1 case
            #prow['doc_pos'] = ppos
            concat_table.set_value(pindex,'doc_pos',ppos)
            concat_table.set_value(pindex,'first_result_type',vert_type)
    
    # Filter rows with page responses. 
    page_responses = concat_table[concat_table['type'] == 'page_response']
    page_responses = page_responses[page_responses['first_result_type'].str.len() == 1]
    print page_responses[page_responses['doc_pos'] ==0].groupby(\
            ['first_result_type', 'response_type']).agg({
                # Find the mean and std rel and satisfaction.
                'response_value' : {
                    'mean': 'mean',
                    'std-dev' : 'std',
                    'count' : 'count'
                }
            })
    print page_responses[page_responses['doc_pos']>0].groupby(\
            ['first_result_type','response_type']).agg({
                # Find the mean and std rel and satisfaction.
                'response_value' : {
                    'mean': 'mean',
                    'std-dev' : 'std',
                    'count' : 'count'
                }
            })

# Update card visibility based on visible_elements
# 1: visible 0: invisible
def UpdateCardVisibility(visible_elements,card_vis):
    card_list = visible_elements.split(' ')
    for card in card_list:
        c = card.split('_')
        if len(c) > 2:
            card_vis[int(c[2])] = 1

    return card_vis

def UpdateCardStatus(visible_elements,card_status,card_time,time):
    inv_cards = range(0,10)
    card_list = visible_elements.split(' ')
    for card in card_list:
        c = card.split('_')
        if len(c) > 2:
            cid = int(c[2])

            # Note the time if the card became visible
            if card_status[cid] == None:
                card_status[cid] = time

            # Remove the card from invisible card list
            inv_cards.remove(cid)

    # Update the time for cards that became invisible
    for cid in inv_cards:
        if card_status[cid] != None:
            card_time[cid] = card_time[cid] + (time-card_status[cid]).total_seconds()
            card_status[cid] = None

    return [card_status, card_time]


def FindVisiblityMetricsPerVertical(result_table,vis_event_table):
    # Consider only top position
    result_table = result_table[result_table['doc_pos']==0]
    # Consider only first page
    result_table = result_table[result_table['page_id']==1]
    merge_table = pd.merge(result_table,vis_event_table,left_on=['user_id','task_id','query_text'],right_on=['user_id','task_id','query_text'])
    merge_table.to_csv('merge_result_vis_event.csv',encoding = 'utf-8',sep = '\t')

    # Initialize visiblity metric
    # Stores #sessions in which 
    # each card was visible
    visibility = {}
    visibility['i'] = np.zeros(10)
    visibility['v'] = np.zeros(10)
    visibility['w'] = np.zeros(10)
    visibility['o'] = np.zeros(10)

    # Initialize time metric
    # Stores the total time 
    # for which each card was visible
    visible_time = {}
    visible_time['i'] = np.zeros(10)
    visible_time['v'] = np.zeros(10)
    visible_time['w'] = np.zeros(10)
    visible_time['o'] = np.zeros(10)

    grouped_table = merge_table.sort(['time_y']).groupby(['user_id','task_id','query_text'])

    for name, group in grouped_table:
        # card visibility for this session
        # 1: visible 0: invisible
        card_vis = np.zeros(10)

        # card status and time for this session
        # card_status stores time when it became visible or 0 if its invisible
        # card_time stores time in seconds
        card_status = 10*[None]
        card_time = np.zeros(10)        
        last_time = 0
        for index, row in group.iterrows():
            card_vis = UpdateCardVisibility(row['event_value'],card_vis)
            top_vert = row['doc_type']

            [card_status, card_time] = UpdateCardStatus(row['event_value'],card_status,card_time,row['time_y'])

            # Stores the time of the last event in this session
            last_time = row['time_y']

        # Update visibility of the vertical
        if sum(card_vis) > 0:
            visibility[top_vert] = visibility[top_vert] + card_vis

            # For now we assume all cards become invisible in the last event
            # So use that time to compute the dwell time of cards that 
            # were visible at the end of the sessions
            # TODO: Ideally we would like to use the time of the first event
            # of the next session
            for cid in range(0,10):
                if card_status[cid] != None:
                    card_time[cid] = card_time[cid] + (last_time - card_status[cid]).total_seconds()
            visible_time[top_vert] = visible_time[top_vert] + card_time

    print 'image',visibility['i']
    print 'video',visibility['v']
    print 'wiki',visibility['w']
    print 'organic',visibility['o']

    print 'image',visible_time['i']
    print 'video',visible_time['v']
    print 'wiki',visible_time['w']
    print 'organic',visible_time['o']


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

    # Format tap event db
    tap_event_table = FormatEventDBForTap(event_db,tap_event_header,tap_event_sortkeys)

    # Format visibility event db
    vis_event_table = FormatEventDBForVisibility(event_db,vis_event_header,vis_event_sortkeys)

    # a. task : users. Compute the number of users who provided task feedback
    # task_id, #users_who_gave_feedback
    #task_response_table[['task_id','user_id']].groupby(['task_id']).\
    #        agg({'user_id': pd.Series.nunique}).to_csv('task_feedback.csv')

    # b. task : user_impressions. Compute the number of users who executed a task.
    # task_id, #users_who_executed_task
    #page_response_table[['task_id','user_id']].groupby(['task_id']).\
    #        agg({'user_id': pd.Series.nunique}).to_csv('task_execute.csv')

    # c. vertical_type : vertical_SERPs. Compute the number of times each vertical was shown as top result.
    # Only consider query results in the first page (page_id==1)
    # Here we output counts for all the doc position in the first page
    # doc_type, #occurances
    query_results = query_table[(query_table['page_id']==1) & \
            (query_table['doc_pos'] == 0)]
    print query_results.groupby(['doc_type'])['task_id'].count()

    # d. vertical_type : queries. Compute the number of queries fired for each vertical.
    # task_id, #unique_queries
    #queries_with_time= query_results[['time','doc_type','query_text']].drop_duplicates();
    #queries_with_time.groupby(['doc_type','query_text']).agg(\
    #        {'query_text': pd.Series.count}).to_csv('vert_queries.csv')

    # f. task : time . Compute the time spent on doing each task.

    # g. task : click_ranks. Compute the number of times a position was clicked
    # ignore positions with double digits as they are nested clicks
    # doc_pos = (page_id - 1) * 10 + doc_id
    # task_id, doc_pos, #clicks
    click_filtered = click_table[click_table['doc_id'].str.len()\
            == 5]
    #click_filtered['doc_pos'] = (click_filtered['page_id'].astype(float) -\
    #        1.0) + (click_filtered['doc_id'].str[4]).astype(float)
    # Filter the columns for count.
    #click_filtered[['task_id','doc_pos']].groupby(['task_id','doc_pos'])['doc_pos'].\
    #        count().to_csv('task_rank_click_counts.csv', encoding = 'utf-8',\
    #        sep = '\t')
    #click_filtered = click_table[click_table['doc_id'].str.len()\
    #        == 5]

    merged_tables = MergeAllTables(query_table, click_filtered, tap_event_table,\
    	 page_response_table, task_response_table)
    
    # Find the vertical_type stats: sessions, queries, clicks a
    # nd average satisfaction/rel values.
    #FindDescriptiveStatsPerVertical(merged_tables)
    
    # h. vertical_type : time_to_first_click_and_position. Compute the time to first click for each
    # k. vertical_type : last_click_position. Compute the ranks that were clicked last for
    FindFirstAndLastClickInfo(merged_tables)
    
    # For every page whose response is available find its doc_pos on serp
    # We ignore the pages who are serp since they do not have any doc_pos
    FindPageMetricsPerVertical(query_table,page_response_table)


    # Generate visibility statistics
    FindVisiblityMetricsPerVertical(query_table,vis_event_table)

if __name__ == "__main__":
    main()
