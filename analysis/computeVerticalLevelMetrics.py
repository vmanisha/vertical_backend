import pandas as pd
import numpy as np
import re
from datetime import datetime
import editdistance 
from scipy.stats.mstats import mannwhitneyu, kruskalwallis,ttest_ind
from plotStats import *

TASKSATMAP = {'Somewhat Satisfied': 2.0, 'Highly Satisfied': 3.0, 'Not Satisfied' : 1.0}

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
    grouped_table = concat_table.sort(['time']).groupby(['user_id','task_id'])
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
    # Print the statistical significance against organic
    print 'Man off_vert_rank i-o', kruskalwallis(vertical_stats['i']['off_vert_rank'],vertical_stats['o']['off_vert_rank'])
    print 'Man off_vert_rank v-o',\
    kruskalwallis(vertical_stats['v']['off_vert_rank'],vertical_stats['o']['off_vert_rank'])
    print 'Man off_vert_rank w-o',\
    kruskalwallis(vertical_stats['w']['off_vert_rank'],vertical_stats['o']['off_vert_rank'])

    print 'Man first_rank  i-o',\
    kruskalwallis(vertical_stats['i']['first_rank'],vertical_stats['o']['first_rank'])
    print 'Man first_rank v-o',\
    kruskalwallis(vertical_stats['v']['first_rank'],vertical_stats['o']['first_rank'])
    print 'Man first_rank w-o',\
    kruskalwallis(vertical_stats['w']['first_rank'],vertical_stats['o']['first_rank'])

    print 'Man lr i-o',\
    kruskalwallis(vertical_stats['i']['last_rank'],vertical_stats['o']['last_rank'])
    print 'Man lr v-o',\
    kruskalwallis(vertical_stats['v']['last_rank'],vertical_stats['o']['last_rank'])
    print 'Man lr w-o',\
    kruskalwallis(vertical_stats['w']['last_rank'],vertical_stats['o']['last_rank'])
    
    print 'Man fc i-o',\
        kruskalwallis(vertical_stats['i']['first_click'],vertical_stats['o']['first_click'])
    print 'Man fc v-o',\
        kruskalwallis(vertical_stats['v']['first_click'],vertical_stats['o']['first_click'])
    print 'Man fc w-o',\
        kruskalwallis(vertical_stats['w']['first_click'],vertical_stats['o']['first_click'])
    
    print 'Man lc i-o',\
        kruskalwallis(vertical_stats['i']['last_click'],vertical_stats['o']['last_click'])
    print 'Man lc v-o',\
        kruskalwallis(vertical_stats['v']['last_click'],vertical_stats['o']['last_click'])
    print 'Man lc w-o',\
        kruskalwallis(vertical_stats['w']['last_click'],vertical_stats['o']['last_click'])
   
        

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
            if row['type'] == 'results' and row['doc_pos'] == 0:
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
                    vertical_stats[doc_type]['task_sat'].append(TASKSATMAP[row['response_value']])
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
        print vertical_type , stat_dict['sess'],\
         'query',np.mean(stat_dict['query']),round(np.std(stat_dict['query']),2), \
        'click', np.mean(stat_dict['clicks']),round(np.std(stat_dict['clicks']),2), \
        'page_rel',np.mean(stat_dict['page_rel']),round(np.std(stat_dict['page_rel']),2),\
        'page_sat', np.mean(stat_dict['page_sat']),round(np.std(stat_dict['page_sat']),2),\
        'task sat', np.mean(stat_dict['task_sat']),round(np.std(stat_dict['task_sat']),2),\
        'time ', np.mean(stat_dict['time']),round(np.std(stat_dict['time']),2)

    # Print the statistical significance against organic
    print 'Man query i-o', kruskalwallis(vertical_stats['i']['query'],vertical_stats['o']['query'])
    print 'Man query v-o', kruskalwallis(vertical_stats['v']['query'],vertical_stats['o']['query'])
    print 'Man query w-o', kruskalwallis(vertical_stats['w']['query'],vertical_stats['o']['query'])

    print 'Man click i-o', kruskalwallis(vertical_stats['i']['clicks'],vertical_stats['o']['clicks'])
    print 'Man click v-o', kruskalwallis(vertical_stats['v']['clicks'],vertical_stats['o']['clicks'])
    print 'Man click w-o', kruskalwallis(vertical_stats['w']['clicks'],vertical_stats['o']['clicks'])

    print 'Man page_rel i-o', kruskalwallis(vertical_stats['i']['page_rel'],vertical_stats['o']['page_rel'])
    print 'Man page rel v-o', kruskalwallis(vertical_stats['v']['page_rel'],vertical_stats['o']['page_rel'])
    print 'Man page rel w-o', kruskalwallis(vertical_stats['w']['page_rel'],vertical_stats['o']['page_rel'])
    
    print 'Man page_sat i-o', kruskalwallis(vertical_stats['i']['page_sat'],vertical_stats['o']['page_sat'])
    print 'Man page_sat v-o',kruskalwallis(vertical_stats['v']['page_sat'],vertical_stats['o']['page_sat'])
    print 'Man page sat w-o', kruskalwallis(vertical_stats['w']['page_sat'],vertical_stats['o']['page_sat'])
    
    print 'Man task_sat i-o', kruskalwallis(vertical_stats['i']['task_sat'],vertical_stats['o']['task_sat'])
    print 'Man task_sat v-o',kruskalwallis(vertical_stats['v']['task_sat'],vertical_stats['o']['task_sat'])
    print 'Man task sat w-o', kruskalwallis(vertical_stats['w']['task_sat'],vertical_stats['o']['task_sat'])
   


    print 'Not registered clicks ', not_registered_clicks

def FindTaskSatPerVertical(result_table,task_table):
    # Consider only satisfaction response
    task_table = task_table[task_table['response_type']=='satisfaction']

    # Join on task_table
    merge_table = pd.merge(result_table,task_table,how='right',left_on=['user_id','task_id'],right_on=['user_id','task_id'])
    merge_table.to_csv('merge.csv',encoding='utf-8', index = False)
    
    satisfaction = {'i':[], 'v':[], 'w':[], 'o':[]}

    for index, row in merge_table.iterrows():
        vert = row['doc_type']

        # Check if the vertical is a valid vertical
        # Need to check this because not all entires in task db
        # has a corresponding entry in result db
        # These are the people who rated task without executing a single query!
        # We have no choice but to ignore their task ratings
        if vert in satisfaction:
            satisfaction[vert].append(TASKSATMAP[row['response_value']])

    print 'statisfaction',satisfaction
    print 'image',np.median(satisfaction['i']),np.mean(satisfaction['i']),np.std(satisfaction['i'])
    print 'video',np.median(satisfaction['v']),np.mean(satisfaction['v']),np.std(satisfaction['v'])
    print 'wiki',np.median(satisfaction['w']),np.mean(satisfaction['w']),np.std(satisfaction['w'])
    print 'organic',np.median(satisfaction['o']),np.mean(satisfaction['o']),np.std(satisfaction['o'])

    PlotTaskSat(satisfaction)


def FindTaskPrefDistribution(task_table):
    task_table = task_table[task_table['response_type']=='preferred_verticals']

    # Compute overall preference and task preference
    overall_preference = {'Wiki':0,'General Web':0,'Videos':0,'Other':0,'Images':0}
    
    # Stores the number of times a task feedback given
    task_count = np.zeros(10)

    # Task prefernce per task_id
    task_preference = []
    for tid in range(0,10):
        task_preference.append({'Wiki':0,'General Web':0,'Videos':0,'Other':0,'Images':0})

    for index, row in task_table.iterrows():
        tid = row['task_id']-1
        task_count[tid] = task_count[tid] + 1

        pref_value = row['response_value']
        pref_list = pref_value.split(',')
        for pref in pref_list:
            pref = pref.strip()
            if pref != '':
                overall_preference[pref] = overall_preference[pref] + 1
                task_preference[tid][pref] = task_preference[tid][pref] + 1

    for tid in range(0,10):
        for key,value in task_preference[tid].iteritems():
            task_preference[tid][key] = float(task_preference[tid][key])/float(task_count[tid])

    print overall_preference
    for pref in task_preference:
        print pref.values()

def FindTaskPrefPerVertical(result_table,task_table):
    task_table = task_table[task_table['response_type']=='preferred_verticals']

    # Join on task_table
    merge_table = pd.merge(result_table,task_table,how='right',left_on=['user_id','task_id'],right_on=['user_id','task_id'])

    vert_preference = {'i':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,'Images':0}, \
        'v':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,'Images':0},\
        'w':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,'Images':0},\
        'o':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,'Images':0},}

    # Stores the number of times a vertical was shown
    vert_count = {'i':0,'v':0,'w':0,'o':0}

    for index, row in merge_table.iterrows():
        vert = row['doc_type']

        if vert in vert_preference:
            vert_count[vert] = vert_count[vert] + 1
            pref_value = row['response_value']
            pref_list = pref_value.split(',')
            for pref in pref_list:
                pref = pref.strip()
                if pref != '':
                    vert_preference[vert][pref] = vert_preference[vert][pref] + 1
 
    for key, value in vert_preference.iteritems():
        for k, v in value.iteritems():
            vert_preference[key][k] = float(vert_preference[key][k])/float(vert_count[key])

    print vert_preference

'''
# TODO: fix clicks by adding data from response or tap db
def FindClickDistributionPerVertical(result_table,click_filtered):
    concat_table = pd.concat([result_table, click_filtered], ignore_index = True)

    grouped_table = concat_table.groupby(['user_id'])

    # Stores the #clicks per positions per vertical
    click_pos = {'i':np.zeros(10), 'v':np.zeros(10), 'w':np.zeros(10), 'o': np.zeros(10)}

    # Stores the click distribution per vertical
    click_dist = {'i':[], 'v':[], 'w':[], 'o': []}

    # Stores the number of times a vertical was shown
    vert_count = {'i':0,'v':0,'w':0,'o':0}

    for name, group in grouped_table:
        group = group.sort(['time'])

        vert = None
        for index, row in group.iterrows():

            # Get the top vertical from result row
            if row['type'] == 'results':
                vert = row['doc_type']
                vert_count[vert] = vert_count[vert] + 1

            # Update clicks from click row
            if row['type'] == 'click':
                # Get the position of the clicked doc
                doc_id = row['doc_id']
                pos = int(doc_id.split('_')[1])
                click_pos[vert][pos] = click_pos[vert][pos] + 1
                click_dist[vert].append(pos+1)

    PlotClickDistPerVertical(click_dist)

    print 'image',' '.join([str(x) for x in click_pos['i']])
    print 'video',' '.join([str(x) for x in click_pos['v']])
    print 'wiki',' '.join([str(x) for x in click_pos['w']])
    print 'organic',' '.join([str(x) for x in click_pos['o']])

    print 'image',' '.join([str(round(float(clicks)/float(vert_count['i']),3)) \
        for clicks in click_pos['i']])
    print 'video',' '.join([str(round(float(clicks)/float(vert_count['v']),3)) \
        for clicks in click_pos['v']])
    print 'wiki',' '.join([str(round(float(clicks)/float(vert_count['w']),3)) \
        for clicks in click_pos['w']])
    print 'organic',' '.join([str(round(float(clicks)/float(vert_count['o']),3)) \
        for clicks in click_pos['o']])
'''
