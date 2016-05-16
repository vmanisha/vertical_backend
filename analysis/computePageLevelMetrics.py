import pandas as pd
import numpy as np
import re
from datetime import datetime
import editdistance 
from plotStats import *
from scipy.stats.mstats import mannwhitneyu, kruskalwallis,ttest_ind

# default dwell time of the card in seconds
DEFAULT_CARD_DWELL_TIME = 1

# max card dwell time in seconds
MAX_CARD_DWELL_TIME = 100

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
    first_rel_group = page_responses[page_responses['doc_pos'] ==0].groupby(\
            ['first_result_type', 'response_type'])
    last_rel_group = page_responses[page_responses['doc_pos']>0].groupby(\
            ['first_result_type','response_type'])

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



    # Calculate the significance of all the numbers.
    print 'Man rel_first_rank i-o',\
    kruskalwallis(first_rel_group.get_group(('i','relevance'))['response_value'],\
                  first_rel_group.get_group(('o','relevance'))['response_value'])
    
    print 'Man rel_first_rank v-o',\
    kruskalwallis(first_rel_group.get_group(('v','relevance'))['response_value'],\
                  first_rel_group.get_group(('o','relevance'))['response_value'])

    print 'Man rel_first_rank w-o',\
    kruskalwallis(first_rel_group.get_group(('w','relevance'))['response_value'],\
                  first_rel_group.get_group(('o','relevance'))['response_value'])

    
    print 'Man sat_first_rank i-o',\
    kruskalwallis(first_rel_group.get_group(('i','satisfaction'))['response_value'],\
                  first_rel_group.get_group(('o','satisfaction'))['response_value'])
    print 'Man sat_first_rank v-o',\
    kruskalwallis(first_rel_group.get_group(('v','satisfaction'))['response_value'],\
                  first_rel_group.get_group(('o','satisfaction'))['response_value'])
    print 'Man sat_first_rank w-o',\
    kruskalwallis(first_rel_group.get_group(('w','satisfaction'))['response_value'],\
                  first_rel_group.get_group(('o','satisfaction'))['response_value'])


    print 'Man rel_off_rank i-o',\
    kruskalwallis(last_rel_group.get_group(('i','relevance'))['response_value'],\
                  last_rel_group.get_group(('o','relevance'))['response_value'])
    
    print 'Man rel_off_rank v-o',\
    kruskalwallis(last_rel_group.get_group(('v','relevance'))['response_value'],\
                  last_rel_group.get_group(('o','relevance'))['response_value'])

    print 'Man rel_off_rank w-o',\
    kruskalwallis(last_rel_group.get_group(('w','relevance'))['response_value'],\
                  last_rel_group.get_group(('o','relevance'))['response_value'])

    
    print 'Man sat_off_rank i-o',\
    kruskalwallis(last_rel_group.get_group(('i','satisfaction'))['response_value'],\
                  last_rel_group.get_group(('o','satisfaction'))['response_value'])
    print 'Man sat_off_rank v-o',\
    kruskalwallis(last_rel_group.get_group(('v','satisfaction'))['response_value'],\
                  last_rel_group.get_group(('o','satisfaction'))['response_value'])
    print 'Man sat_off_rank w-o',\
    kruskalwallis(last_rel_group.get_group(('w','satisfaction'))['response_value'],\
                  last_rel_group.get_group(('o','satisfaction'))['response_value'])


    # Find the variation in page satisfaction and relevance for 
    # each position per vertical. 
    rank_level_rel_and_sat = page_responses[page_responses['doc_pos']< 3].groupby(\
            ['first_result_type', 'response_type', 'doc_pos']).agg({
                # Find the mean and std rel and satisfaction.
                'response_value' : {
                    'mean': 'mean',
                    'std-dev' : 'std',
                    'count' : 'count'
                }
            })
    rank_level_rel_and_sat.reset_index().to_csv('vert_level_pos_level_rel_and_sat.csv',index='False')

    # PlotPageResponsePerVert(first_rel_group,last_rel_group)

# Update card visibility based on visible_elements
# 1: visible 0: invisible
def UpdateCardVisibility(visible_elements,card_vis):
    card_list = visible_elements.split(' ')
    for card in card_list:
        c = card.split('_')
        if len(c) > 2:
            card_vis[int(c[2])] = 1

    return card_vis

def UpdateCardTime(visible_elements,card_status,card_time,time):
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
            time_diff = (time-card_status[cid]).total_seconds()
            if time_diff < MAX_CARD_DWELL_TIME:
                card_time[cid] = card_time[cid] + time_diff
            else:
                print 'Time diff > 150', time_diff
                # Something went wrong so setting the dwell time to default
                card_time[cid] = card_time[cid] + DEFAULT_CARD_DWELL_TIME
            card_status[cid] = None

    return card_status, card_time

def FindVisiblityMetricsPerVertical(result_table,vis_event_table):
    concat_table = pd.concat([result_table, vis_event_table], ignore_index = True)

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
    visible_time['i'] ={ 0: [], 1: [] , 2: [], 3: [], 4: [] ,5:[], 6:[], 7:[], 8:[],9:[]} 
    visible_time['v'] ={ 0: [], 1: [] , 2: [], 3: [], 4: [] ,5:[], 6:[], 7:[], 8:[],9:[]} 
    visible_time['w'] ={ 0: [], 1: [] , 2: [], 3: [], 4: [] ,5:[], 6:[], 7:[], 8:[],9:[]} 
    visible_time['o'] ={ 0: [], 1: [] , 2: [], 3: [], 4: [] ,5:[], 6:[], 7:[], 8:[],9:[]}

    grouped_table = concat_table.groupby(['user_id'])
    
    for name, group in grouped_table:
        group = group.sort('time')

        # Top vertical in the session
        top_vert = None

        # time of the previous event in the session
        prev_time = None

        # card visibility for the session
        # 1: visible 0: invisible
        card_vis = np.zeros(10)
    
        # card status and time for the session
        # card_status stores time when it became visible or 0 if its invisible
        # card_time stores time in seconds
        card_status = 10*[None]
        card_time = np.zeros(10)

        # Process sessions for this user
        for index, row in group.iterrows():

            # Row type 'result' indicates the start of a new session
            if row['type'] == 'results':
                
                # Save results of a previous session
                if top_vert != None:
                    visibility[top_vert] = visibility[top_vert] + card_vis
                    card_vis = np.zeros(10)

                    # Compute the time for cards that were visible 
                    # at the end of the previous session
                    for cid in range(0,10):
                        if card_status[cid] != None:
                            time_diff = (row['time']-card_status[cid]).total_seconds()

                            if time_diff < MAX_CARD_DWELL_TIME:
                                card_time[cid] = card_time[cid] + time_diff
                            else:
                                time_diff = (prev_time-card_status[cid]).total_seconds()
                                if time_diff < MAX_CARD_DWELL_TIME:
                                    card_time[cid] = card_time[cid] + time_diff
                                else:
                                    # setting the dwell time to default
                                    card_time[cid] = card_time[cid] + DEFAULT_CARD_DWELL_TIME

                        visible_time[top_vert][cid].append(card_time[cid])

                    card_status = 10*[None]
                    card_time = np.zeros(10)
                    
                top_vert = row['doc_type']

            # Otherwise it is the event row
            # Update stats of the current session
            else:
                card_vis = UpdateCardVisibility(row['event_value'],card_vis)
                card_status, card_time = UpdateCardTime(row['event_value'],card_status,card_time,row['time'])

            prev_time = row['time']

        # Save results of the last session of this user
        if top_vert != None:
            visibility[top_vert] = visibility[top_vert] + card_vis

            # This is the last session of this user
            # so we do not have enough information
            # to compute dwell time for the cards
            # that were visible at the end of the session
            # We simply add default card dwell time
            for cid in range(0,10):
                if card_status[cid] != None:
                    card_time[cid] = card_time[cid] + DEFAULT_CARD_DWELL_TIME
                visible_time[top_vert][cid].append(card_time[cid])


    print 'image',visibility['i']
    print 'video',visibility['v']
    print 'wiki',visibility['w']
    print 'organic',visibility['o']

    print 'image',' '.join([str(round(sum(card_times)/visibility['i'][0],3)) for card_times in
      visible_time['i'].values()])
    print 'video',' '.join([ str(round(sum(card_times)/visibility['v'][0],3)) for card_times in
      visible_time['v'].values()])
    print 'wiki',' '.join([ str(round(sum(card_times)/visibility['w'][0],3)) for card_times in
      visible_time['w'].values()])
    print 'organic',' '.join([str(round(sum(card_times)/visibility['o'][0],3)) for card_times in
      visible_time['o'].values()])

    print 'image',' '.join([str(round(np.median(card_times),3)) for card_times in
      visible_time['i'].values()])
    print 'video',' '.join([ str(round(np.median(card_times),3)) for card_times in
      visible_time['v'].values()])
    print 'wiki',' '.join([ str(round(np.median(card_times),3)) for card_times in
      visible_time['w'].values()])
    print 'organic',' '.join([str(round(np.median(card_times),3)) for card_times in
      visible_time['o'].values()])

    # find stats significance
    print 'Man visibilit time 1 i-o',\
    kruskalwallis(visible_time['i'][0],visible_time['o'][0])
    print 'Man visibilit time 1 v-o',\
    kruskalwallis(visible_time['v'][0],visible_time['o'][0])
    print 'Man visibilit time 1 w-o',\
    kruskalwallis(visible_time['w'][0],visible_time['o'][0])
    
    print 'Man visibilit time 2 i-o',\
    kruskalwallis(visible_time['i'][1],visible_time['o'][1])
    print 'Man visibilit time 2 v-o',\
    kruskalwallis(visible_time['v'][1],visible_time['o'][1])
    print 'Man visibilit time 2 w-o',\
    kruskalwallis(visible_time['w'][1],visible_time['o'][1])
    
    print 'Man visibilit time3  i-o',\
    kruskalwallis(visible_time['i'][2],visible_time['o'][2])
    print 'Man visibilit time 3 v-o',\
    kruskalwallis(visible_time['v'][2],visible_time['o'][2])
    print 'Man visibilit time 3 w-o',\
    kruskalwallis(visible_time['w'][2],visible_time['o'][2])


    print 'Man visibilit time 4  i-o',\
    kruskalwallis(visible_time['i'][3],visible_time['o'][3])
    print 'Man visibilit time 4 v-o',\
    kruskalwallis(visible_time['v'][3],visible_time['o'][3])
    print 'Man visibilit time 4 w-o',\
    kruskalwallis(visible_time['w'][3],visible_time['o'][3])
    
    PlotVisiblityStats(visibility,visible_time)

 
# Find mean and std dwell time per vertical. 
def FindDwellTimes(concat_table):
    vertical_stats = { 'i' : { 'on_dwell': [], 'off_dwell':[] ,\
                  'on_count':0.0, 'off_count':0.0, \
                  'pos_dwell' : {0:[],1:[], 2:[], 3:[], 4:[]},\
                  'all_clicks':[], \
                  'clicks':{0:0.0,1:0.0, 2: 0.0, 3:0.0, 4:0.0}}, \
            'w' : { 'on_dwell': [], 'off_dwell':[],'on_count':0.0,\
                    'off_count':0.0 ,'all_clicks':[],\
                    'pos_dwell' : {0:[],1:[], 2:[], 3:[], 4:[]} ,\
                    'clicks':{0:0.0,1:0.0, 2: 0.0, 3:0.0, 4:0.0}}, \
            'o' : { 'on_dwell': [], 'off_dwell':[],'on_count':0.0,\
                    'off_count':0.0,'pos_dwell' : {0:[],1:[], 2:[], 3:[], 4:[]},\
                    'all_clicks':[],\
                    'clicks':{0:0.0,1:0.0, 2: 0.0, 3:0.0, 4:0.0}  }, \
            'v' : { 'on_dwell': [], 'off_dwell':[],'on_count':0.0,\
                    'off_count':0.0 ,'all_clicks':[], \
                    'pos_dwell' : {0:[],1:[], 2:[], 3:[], 4:[]},\
                    'clicks':{0:0.0,1:0.0, 2: 0.0, 3:0.0, 4:0.0},  \
                  } \
    }

    # Group by task_id and query_id and Sort by time within each group.
    grouped_table = concat_table.groupby(['user_id','task_id'])
    recorded_clicks = {}
    vert_type = None
    for name, group in grouped_table:
        group = group.sort('time')
        rows = []
        results = {}
        serp_clicks = 0
        for index, row in group.iterrows():
            rows.append(row)
        for i in range(len(rows)):
            row = rows[i]
            # Store results.
            if row['type'] == 'results':
                results[row['doc_pos']] = row

            if row['type'] == 'results' and row['doc_pos'] == 0:
                # For each page find time it was tapped or clicked. 
                # Take the min for dwell time.
                vtype = None
                for curl, stats in recorded_clicks.items():
                    vtype = stats['type']
                    if stats['rank'] < 5:
                        vertical_stats[stats['type']]['pos_dwell'][stats['rank']].append(min(stats['time']))
                        vertical_stats[stats['type']]['clicks'][stats['rank']]+=1

                    if stats['rank'] == 0:
                        vertical_stats[stats['type']]['on_dwell'].append(min(stats['time']))
                        vertical_stats[stats['type']]['on_count']+=1.0
                    else:
                        vertical_stats[stats['type']]['off_dwell'].append(min(stats['time']))
                        vertical_stats[stats['type']]['off_count']+=1.0
                if vtype and serp_clicks > 0:
                    vertical_stats[vtype]['all_clicks'].append(serp_clicks)
                recorded_clicks = {}
                serp_clicks = 0
                vert_type = str(row['doc_type']).strip()

            # Found a tap or a click
            start_time  = row['time']
            end_time = None
            found = False
            click_rank = None
            click_url = None
            if (row['type'] == 'event_response') or (row['type'] == 'click') :
                if (row['type'] == 'event_response'):
                    click_url = results[row['event_value']]['doc_url']
                    click_rank = int(row['event_value'])
                if (row['type'] == 'click'):
                    click_rank = int(row['doc_id'][row['doc_id'].find('_')+1:])
                    click_url = row['doc_url']
                # Check if page response for this url has been submitted.
                j = i+1
                while (j < len(rows)) and (not (rows[j]['type'] == 'results')):
                    if rows[j]['type'] == 'page_response':
                        if (rows[j]['doc_url'] in click_url) or\
                        editdistance.eval(click_url, rows[j]['doc_url']) < 20:
                            found = True
                            end_time = rows[j]['time']
                            break
                    if rows[j]['type'] == 'task_response':
                        # user did not provide page or serp feedback :(
                        found = True
                        end_time = rows[j]['time']
                        break
                    if found :
                        break
                    j+=1
                if found and end_time:
                    if click_url not in recorded_clicks:
                        recorded_clicks[click_url] ={'rank':None, 'type':None,
                               'time':[]}
                    recorded_clicks[click_url]['time'].append((end_time-start_time).total_seconds())
                    recorded_clicks[click_url]['rank']= click_rank
                    recorded_clicks[click_url]['type']= vert_type
                    serp_clicks+=1.0
                else:
                    print 'Cannot find in responses', click_url,\
                        row['user_id'], row['task_id'], row['type']

    for vertical, val_dict in vertical_stats.items():
        print vertical, 'on-dwell',np.mean(val_dict['on_dwell']),\
        np.std(val_dict['on_dwell']),'off-dwell', np.mean(val_dict['off_dwell']), \
        np.std(val_dict['off_dwell']), val_dict['on_count'],\
        val_dict['off_count']
    
    # find stats significance
    print 'Man on_dwell i-o',\
    kruskalwallis(vertical_stats['i']['on_dwell'],vertical_stats['o']['on_dwell'])
    print 'Man on_dwell v-o',\
    kruskalwallis(vertical_stats['v']['on_dwell'],vertical_stats['o']['on_dwell'])
    print 'Man on_dwell w-o',\
    kruskalwallis(vertical_stats['w']['on_dwell'],vertical_stats['o']['on_dwell'])

    # find stats significance
    print 'Man off_dwell i-o',\
    kruskalwallis(vertical_stats['i']['off_dwell'],vertical_stats['o']['off_dwell'])
    print 'Man off_dwell v-o',\
    kruskalwallis(vertical_stats['v']['off_dwell'],vertical_stats['o']['off_dwell'])
    print 'Man off_dwell w-o',\
    kruskalwallis(vertical_stats['w']['off_dwell'],vertical_stats['o']['off_dwell'])

    for vert_type, stats in vertical_stats.items():
        for pos , array in stats['pos_dwell'].items():
            print 'Man pos dwell ',vert_type, pos,\
            kruskalwallis(array,vertical_stats['o']['pos_dwell'][pos])

    print 'Man off_dwell i-o',\
    kruskalwallis(vertical_stats['i']['all_clicks'],vertical_stats['o']['all_clicks'])
    print 'Man off_dwell v-o',\
    kruskalwallis(vertical_stats['v']['all_clicks'],vertical_stats['o']['all_clicks'])
    print 'Man off_dwell w-o',\
    kruskalwallis(vertical_stats['w']['all_clicks'],vertical_stats['o']['all_clicks'])
    
    # PlotDwellTimePerVert(vertical_stats)
    # PlotClickDistPerVertical(vertical_stats)
    #PlotPageResponsePerVert(vertical_stats, vertical_stats)
