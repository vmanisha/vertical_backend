import pandas as pd
import numpy as np
from computePageLevelMetrics import *


def CheckEqualVisEle(prev_vis, curr_vis):
    for i in range(len(curr_vis)):
        if prev_vis[i] != curr_vis[i]:
            return False
    return True


# Find the box plot of %page scrolled per vertical. 
def FindPageScrollDistributionPerVertical(result_table, event_table):
    # concat the tables. 
    # For each result page, compute the max pixel scrolled.
    # Take the percentage with page length. 

    result_table['type'] = 'results'
    event_table['type'] = 'event'
    concat_table = pd.concat([result_table, event_table], ignore_index = False)
    
    grouped_table = concat_table.groupby(['user_id','task_id'])
    
    swipe_dist = {'i': {}, 'v': {}, 'w': {}, 'o': {}}
    swipe_freq = {'i': {}, 'v': {}, 'w': {}, 'o': {}}


    # Iterate over all users and tasks
    for name, group in grouped_table:
        group = group.sort('time')
        serp_swipe_dist = {}
        serp_swipe_freq = {}
        # Set vertical type for each serp. 
        vert_type = None
        # Iterate over all rows (with results and events)
        # for a specific user and a task
        for index, row in group.iterrows():
            if row['type'] == 'results' and row['doc_pos'] == 0:
                # update the vertical level stats
                if vert_type:
                    for key in serp_swipe_dist.keys():
                        if key not in swipe_dist[vert_type]:
                            swipe_dist[vert_type][key] = []
                            swipe_freq[vert_type][key] = []
                        swipe_dist[vert_type][key].append(serp_swipe_dist[key])
                        swipe_freq[vert_type][key].append(serp_swipe_freq[key])
                    serp_swipe_dist = {}
                    serp_swipe_freq = {}

                vert_type = row['doc_type']

            if row['type'] == 'event':
                # Compute the elements visible.
                curr_event = row['event_type']
                if curr_event not in serp_swipe_dist:
                    serp_swipe_dist[curr_event] = 0.0
                    serp_swipe_freq[curr_event] = 0.0

                # Check if curr_event and curr_vis same as prev.
                # Just add the distance. 
                if 'swipe' not in curr_event:
                    serp_swipe_dist[curr_event] += row['event_dist']/row['page_height']
                else:
                    serp_swipe_dist[curr_event] += row['event_dist']

                serp_swipe_freq[curr_event] +=1.0

    for vert_type, stats in swipe_dist.items():
        for event_type, values in stats.items():
            print 'Percentage ',vert_type, event_type, np.mean(values), np.std(values)

    for vert_type, stats in swipe_freq.items():
        for event_type, values in stats.items():
            print 'Frequency', vert_type, event_type, np.mean(values), np.std(values)

