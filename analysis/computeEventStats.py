import pandas as pd
import numpy as np
from computePageLevelMetrics import *
from plotStats import PlotXYScatter

def ComputeScrollDistributionBeforeClick(merged_table):
  scroll_events = ['panup', 'pandown']
  grouped_table = merged_table.groupby(['user_id','task_id'])
  tfc_swipe_dist = {'i':[], 'v':[], 'w':[], 'o':[]}
  serp_response_dist = {'i':[], 'v':[], 'w':[], 'o':[]}
  for name, group in grouped_table:
    group = group.sort('time')
    first_result_type = None
    first_event_time = None
    first_click_time = None
    first_click = False
    # It is a tuple of (relevance, satisfaction)
    serp_response = None
    swipe_count = 0.0
    post_click_swipe = 1
    for index, row in group.iterrows():
      if row['type'] == 'results':
        # Update scroll stats for page
        if first_click:
          print first_result_type, swipe_count, post_click_swipe,\
          swipe_count/post_click_swipe
          tfc_swipe_dist[first_result_type].append((first_click_time,\
          swipe_count, swipe_count/(post_click_swipe)))
        # Set everything to null.
        first_result_type = None
        first_event_time = None
        first_click_time = None
        first_click = False
        serp_response = None
        swipe_count = 0.0
        post_click_swipe = 1
        # Set the value
        first_result_type = row['doc_type']
      if row['type'] == 'event' and (not first_event_time):
        first_event_time = row['time']
      if (row['type'] == 'event') and (row['event_type'] in scroll_events) \
      and (not first_click):
        swipe_count+=1
      if (row['type'] == 'event') and (row['event_type'] in scroll_events) \
      and (first_click):
        post_click_swipe+=1.0
      # append clicks. 
      if row['type'] == 'click' and (not first_click):
        first_click = True
        first_click_time =(row['time']-first_event_time).total_seconds()
    if first_click:
      print first_result_type, swipe_count, post_click_swipe,\
          swipe_count/post_click_swipe
      tfc_swipe_dist[first_result_type].append((first_click_time,\
     swipe_count, swipe_count/(post_click_swipe)))
  
    # It should ideally be short or long scrolls. Time between two scrolls. 
  scatter1 = {}
  swipe_ratio_per_vertical = {'i':[], 'v':[], 'w':[], 'o':[]}
  for result_type, time_and_swipe_array in tfc_swipe_dist.items():
    print result_type, len(time_and_swipe_array)
    # format vert_type : [[x], [y]]
    scatter1[result_type] = [[],[]]
    # Sort by time (the format is time, pos, last_viewd_rank)
    sorted_tuple_by_time = sorted(time_and_swipe_array, key = lambda x : x[0])
    for sorted_tuple in sorted_tuple_by_time:
      # Add time
      if sorted_tuple[0] < 55 and sorted_tuple[2] < 35:
        scatter1[result_type][0].append(sorted_tuple[0])
        # Add click rank
        scatter1[result_type][1].append(sorted_tuple[2])
        swipe_ratio_per_vertical[result_type].append(sorted_tuple[2])
  #PlotScrollDepthPerVert(swipe_ratio_per_vertical,' Verticals',\
  #    'Pre-Post Click Swipe Down Ratio','Swipe Down Ratio Per Vertical',\
  #    'pre_post_swipe_down_ratio.png')

  print 'Man click i-o', kruskalwallis(swipe_ratio_per_vertical['i'],swipe_ratio_per_vertical['o'])
  print 'Man click v-o', kruskalwallis(swipe_ratio_per_vertical['v'],swipe_ratio_per_vertical['o'])
  print 'Man click w-o', kruskalwallis(swipe_ratio_per_vertical['w'],swipe_ratio_per_vertical['o'])


def CheckEqualVisEle(prev_vis, curr_vis):
    for i in range(len(curr_vis)):
        if prev_vis[i] != curr_vis[i]:
            return False
    return True

def FindPageVelocityDistribution(result_table, event_table):
    # Find velocity distribution per serp.
    scroll_events = ['panup','pandown', 'swipeup','swipedown',\
            'panleft','panright']
    verticals = ['i','v','w','o']

    result_table['type'] = 'results'
    event_table['type'] = 'event'
    # Will contain dictionary of time : velocity. 
    #speedx_buckets = {'i':[], 'v':[] ,'w':[], 'o':[]}
    #speedy_buckets = {'i':[], 'v':[] ,'w':[], 'o':[]}
    # Will contain list of time of swipe in seconds from the beginning.   
    swipe_time_buckets = {'i':[], 'v':[] ,'w':[], 'o':[]}

    concat_table = pd.concat([result_table, event_table], ignore_index = False)
    grouped_table = concat_table.groupby(['user_id','task_id'])
    for name, group in grouped_table:
        group = group.sort('time')
        # Set vertical type for each serp. 
        vert_type = None
        swipe_time = {}
        clicked = False
        last_action = None
        #speeds_x = {}
        #speeds_y = {}
        start_time = None
        for index, row in group.iterrows():
            if row['type'] == 'results' and row['doc_pos'] == 0:
                # update the vertical level stats
                if vert_type:
                    #speedx_buckets[vert_type].append(speeds_x)
                    #speedy_buckets[vert_type].append(speeds_y)
                    swipe_time_buckets[vert_type].append(swipe_time)
                vert_type = row['doc_type']
                swipe_time = {}
                #speeds_x = {}
                #speeds_y = {}
                start_time = row['time']
                last_action = 'start'
            
            if row['type'] == 'event' and (('click' in row['event_type']) or\
                    ('tap' in row['event_type'])) and not clicked:
                        swipe_time['first_click'] = (event_time - start_time).total_seconds()
                        last_action = 'click'
                        clicked = True

            if row['type'] == 'event' and row['event_type'] in scroll_events:
                event_time = row['time']
                # Append the speed. 
                #speeds_x[(event_time - start_time).total_seconds()] =\
                #    row['event_x']
                #speeds_y[(event_time - start_time).total_seconds()] =\
                #    row['event_y']

                # Append the time for frequency.
                if start_time and last_action!=row['direction']:
                    swipe_time[(event_time - start_time).total_seconds()] = row['direction']
                last_action = row['direction']

        if vert_type:
            #speedx_buckets[vert_type].append(speeds_x)
            #speedy_buckets[vert_type].append(speeds_y)
            swipe_time_buckets[vert_type].append(swipe_time)
    
    aggregate_freq = {'i': {} , 'v':{} , 'w': {}, 'o':{}}
    freq_per_time_bucket = {'i':{'percent_action':[]},\
                            'v':{'percent_action':[]} ,\
                            'w':{'percent_action':[]},\
                            'o':{'percent_action':[]}}
    curr_dirn = 'up'
    for  vert_type, time_stamps in swipe_time_buckets.items():
        # take max time (last swipe)
        for time_dict in time_stamps:
            action_freq_bfc = 0.0 
            action_freq_afc = 0.0 
            total_dirn = 0.0
            print sorted(time_dict.items(), key = lambda x : x[0])
            if len(time_dict) > 0 and 'first_click' in time_dict:
                first_click_time = time_dict['first_click']
                #max_time = max(time_dict.keys())
                #total = len(time_dict)
                #bucket_size = max_time/10
                #bucket = {}
                for time, dirn in time_dict.items():
                    if dirn == curr_dirn:
                        total_dirn+=1.0
                        if time < first_click_time:
                            action_freq_bfc+=1.0
                        else:
                            action_freq_afc+=1.0

                    #index = int((time/bucket_size))
                    #if index not in bucket:
                    #    bucket[index] = 0.0
                    #if dirn == 'up':
                    #bucket[index]+= (1.0 / total)
                
                freq_per_time_bucket[vert_type]['percent_action'].append(action_freq_bfc/(action_freq_afc+1))
                '''
                for index, count in bucket.items():
                    if index not in aggregate_freq[vert_type]:
                        aggregate_freq[vert_type][index]= []
                    aggregate_freq[vert_type][index].append(count)
                '''
    PlotVerticalLevelAttributeBoxPlot(freq_per_time_bucket, 'percent_action',\
            8,['Swipe Up'], 'Before/after first click swipe ratio', '',\
            'swipe_up_percentage_before_click.png')
    for v1 in ['i' , 'v' , 'w', 'o']:
        for v2 in ['i' , 'v' , 'w', 'o']:
            print v1, v2, kruskalwallis(freq_per_time_bucket[v1]['percent_action'],\
                    freq_per_time_bucket[v2]['percent_action']),\
            np.mean(freq_per_time_bucket[v1]['percent_action']),\
            np.std(freq_per_time_bucket[v1]['percent_action']),\
            np.mean(freq_per_time_bucket[v2]['percent_action']),\
            np.std(freq_per_time_bucket[v2]['percent_action'])
    #PlotMultipleBoxPlotsPerVertical(freq_per_time_bucket, [5,10,20,'>20'],'Time (sec)',\
    #                              'Gesture Frequency','','gesture_frequency_with_time.png')
    # PlotVertSwipeInfoByTime(aggregate_freq, 'Time buckets','Normalized Swipe Freq')
    '''
    aggregate_speed_x = {'i': {} , 'v':{} , 'w': {}, 'o':{}}
    aggregate_speed_y = {'i': {} , 'v':{} , 'w': {}, 'o':{}}

    for vert_type, speed_list in speedx_buckets.items():
        bucket = AggregateSpeedsWithTime(speed_list)
        for index, speeds in bucket.items():
            if index not in aggregate_speed_x[vert_type]:
                aggregate_speed_x[vert_type][index] = []
            aggregate_speed_x[vert_type][index] = bucket[index]
    PlotVertSwipeInfoByTime(aggregate_speed_x, 'Time buckets','Swipe Velocity in X-dim')
    
    for vert_type, speed_list in speedy_buckets.items():
        bucket = AggregateSpeedsWithTime(speed_list)
        for index, speeds in bucket.items():
            if index not in aggregate_speed_y[vert_type]:
                aggregate_speed_y[vert_type][index] = []
            aggregate_speed_y[vert_type][index] = bucket[index]
    PlotVertSwipeInfoByTime(aggregate_speed_y, 'Time buckets','Swipe Velocity in Y-dim')
    '''
'''
@speeds : An array of dictionaries of format: {time_from_result_display: speed}
'''
def AggregateSpeedsWithTime(speeds):

    bucket = {};
    for speed_dict in speeds:
        total = len(speed_dict)
        if total > 0:
            max_time = max(speed_dict.keys())
            bucket_size = max_time/10
            for entry, speed in speed_dict.items():
                index = int(entry/bucket_size)
                if index not in bucket:
                    bucket[index] = []
                bucket[index].append(speed)
    return bucket;
            


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
    
    # PlotSwipeDataPerVert(swipe_freq, 'panup','pandown',['Down', 'Up'],\
    #                      'Swipe Direction','Swipe Frequency',45,\
    #                      'swipe_freq.png')
    # PlotSwipeDataPerVert(swipe_dist, 'panup','pandown',['Down', 'Up'],\
    #                      'Swipe Direction','Swipe Distance (px)',6500,\
    #                      'swipe_dist.png')
