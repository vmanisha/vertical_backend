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

    scroll_events = ['panup','pandown','panleft','panright','swipeleft','swiperight']
    verticals = ['i','v','w','o']

    result_table['type'] = 'results'
    event_table['type'] = 'event'
    concat_table = pd.concat([result_table, event_table], ignore_index = False)
    
    grouped_table = concat_table.groupby(['user_id','task_id'])
    
    swipe_dist = {}
    swipe_freq = {}
    for vert in verticals:
        swipe_dist[vert] = {}
        swipe_freq[vert] = {}
        for event in scroll_events:
            swipe_dist[vert][event] = []
            swipe_freq[vert][event] = []
    

    # Fraction of serp in which user swiped
    serp_freq = {'i': 0, 'v': 0, 'w': 0, 'o': 0}
    serp_swipe = {'i':{'left':0, 'right':0, 'any':0}, \
        'v':{'left':0, 'right':0, 'any':0},
        'w':{'left':0, 'right':0, 'any':0},
        'o':{'left':0, 'right':0, 'any':0}}

    # Depth of scrolling based on highest (farthest in serp) visited card
    max_scroll_card = {'i': [], 'v': [], 'w': [], 'o': []}
    max_vis_card = {'i': [], 'v': [], 'w': [], 'o': []}

    # Iterate over all users and tasks
    for name, group in grouped_table:
        group = group.sort('time')
        serp_swipe_dist = {}
        serp_swipe_freq = {}
        for event in scroll_events:
            serp_swipe_dist[event] = 0.0
            serp_swipe_freq[event] = 0.0
        serp_swipe_left = False
        serp_swipe_right = False
        serp_max_scroll_card = 1
        serp_max_vis_card = 1
        # Set vertical type for each serp. 
        vert_type = None
        # Iterate over all rows (with results and events)
        # for a specific user and a task
        for index, row in group.iterrows():
            if row['type'] == 'results' and row['doc_pos'] == 0:
                # update the vertical level stats
                if vert_type:
                    for event in scroll_events:
                        swipe_dist[vert_type][event].append(serp_swipe_dist[event])
                        swipe_freq[vert_type][event].append(serp_swipe_freq[event])
                        serp_swipe_dist[event] = 0.0
                        serp_swipe_freq[event] = 0.0

                    # Update serp freq and swipe status
                    serp_freq[vert_type] += 1
                    if serp_swipe_left:
                        serp_swipe[vert_type]['left'] += 1
                    if serp_swipe_right:
                        serp_swipe[vert_type]['right'] += 1
                    if serp_swipe_left or serp_swipe_right:
                        serp_swipe[vert_type]['any'] += 1
                    serp_swipe_left = False
                    serp_swipe_right = False

                    # Update scroll depth
                    max_scroll_card[vert_type].append(float(serp_max_scroll_card+1)/10.0)
                    serp_max_scroll_card = 1
                    max_vis_card[vert_type].append(float(serp_max_vis_card+1)/10.0)
                    serp_max_vis_card = 1

                vert_type = row['doc_type']

            if row['type'] == 'event':
                # Compute the elements visible.
                curr_event = row['event_type']

                # Check if curr_event and curr_vis same as prev.
                # Just add the distance. 
                # if 'swipe' not in curr_event:
                #     serp_swipe_dist[curr_event] += row['event_dist']/row['page_height']
                # else:
                #     serp_swipe_dist[curr_event] += row['event_dist']
                serp_swipe_dist[curr_event] += row['event_dist']
                serp_swipe_freq[curr_event] += 1.0

                # Check if user swiped
                if curr_event == 'swipeleft':
                    serp_swipe_left = True
                elif curr_event == 'swiperight':
                    serp_swipe_right = True

                # If user scrolled down
                # update the max visible card
                if 'pan' in curr_event:
                    card = row['event_value']
                    if card > serp_max_scroll_card:
                        serp_max_scroll_card = card

                # Update max card based on visible elements
                visible_elements = row['visible_elements']
                card_list = visible_elements.split(' ')
                for card in card_list:
                    card_id = card.split('_')
                    if len(card_id) > 2 and card_id[2] > serp_max_vis_card:
                        serp_max_vis_card = int(card_id[2])


        if vert_type:
            for event in scroll_events:
                swipe_dist[vert_type][event].append(serp_swipe_dist[event])
                swipe_freq[vert_type][event].append(serp_swipe_freq[event])
                serp_swipe_dist[event] = 0.0
                serp_swipe_freq[event] = 0.0

            # Update serp freq and swipe status
            serp_freq[vert_type] += 1
            if serp_swipe_left:
                serp_swipe[vert_type]['left'] += 1
            if serp_swipe_right:
                serp_swipe[vert_type]['right'] += 1
            if serp_swipe_left or serp_swipe_right:
                serp_swipe[vert_type]['any'] += 1
            serp_swipe_left = False
            serp_swipe_right = False

            # Update scroll depth
            max_scroll_card[vert_type].append(float(serp_max_scroll_card+1)/10.0)
            serp_max_scroll_card = 1
            max_vis_card[vert_type].append(float(serp_max_vis_card+1)/10.0)
            serp_max_vis_card = 1


    for vert_type, stats in swipe_dist.items():
        for event_type, values in stats.items():
            print 'Percentage ',vert_type, event_type, round(np.mean(values),2), round(np.std(values),2)

    for vert_type, stats in swipe_freq.items():
        for event_type, values in stats.items():
            print 'Frequency', vert_type, event_type, round(np.mean(values),2), round(np.std(values),2)

    for vert_type, values in max_vis_card.items():
        print 'Depth', vert_type, round(np.mean(values),2), round(np.std(values),2)

    # print swipe_dist
    # print swipe_freq

    # print serp_freq
    # print serp_swipe
    # print max_scroll_card
    # print max_vis_card

    # PlotScrollDepthPerVert(max_scroll_card)
    # PlotScrollDepthPerVert(max_vis_card)
    
    # PlotSwipeFreqPerVert(swipe_freq)
    # PlotSwipeDistPerVert(swipe_dist)