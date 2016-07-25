import pandas as pd
import numpy as np
import re
from datetime import datetime
import editdistance 
from scipy.stats.mstats import mannwhitneyu, kruskalwallis,ttest_ind
from plotStats import *
import math

TASKSATMAP = {'Somewhat Satisfied': 2.0, 'Highly Satisfied': 3.0, 'Not Satisfied' : 1.0}

def GetSERPSatisfactionCorrelationPerVertical(merged_table):
    grouped_table = merged_table.groupby(['user_id','task_id'])
    # Find the correlation between the following and satisfaction :
        # number of swipes up
        # number of swipe down
        # reformulation
        # number of clicked results
        # total time on SERP
        # Last depth viewed before first click.
        # first clicked rank.
        # distance of swipe up/number of swipe up
        # distance of swipe down/number of swipe down
        # time to first click. 
        # time to last click 
        # screen time of first 3 results
        # screen time of 3-6 results
        # screen time of rest of results. 
    
    # Serp level response does not contain the result type on type. 
    # thus tie it to the query. 
    for name, group in grouped_table:
        group = group.sort('time')
        serp_score_and_features = {}
        query_result_type_string = None
        for index, row in group.iterrows():
            if row['type'] == 'results':
                # Update the previous query and type features with
                # reformulation.
                if query_result_type_string:
                    serp_score_and_features[query_result_type_string]['reformulate']= 1.0
                # Initialize the key. 
                first_result_type = row['doc_type']
                query =  row['query_text']
                query_result_type_string = first_result_type+'_'+\
                                            query.replace(' ','_')
                if query_result_type_string not in serp_score_and_features:
                    serp_score_and_features[query_result_type_string] = {}
            if row['type'] == 'event':
                # Add first event time. 
                event_type = row['event_type']
                serp_score_and_features[query_result_type_string] = AddSerpFeature(\
                        'first_event_time',serp_score_and_features[query_result_type_string],\
                        row['time'])
                # Add event counts. 
                if ('tap' in event_type) or ('pan' in event_type) or ('swipe'\
                        in event_type):
                    serp_score_and_features[query_result_type_string] =\
                            AddOrUpdateSerpFeature(event_type+'_count',\
                            serp_score_and_features[query_result_type_string],1.0)
                # Add visibility of results 
                
                    

# Add a feature to serp only if it does not exist. Useful to add time oriented
# features such as first click/event/tap time. 
def AddSerpFeature(event_type, serp_event_dict, event_value):
    if event_type not in serp_event_dict:
        serp_event_dict[event_type] = event_value
    return serp_event_dict

# If the feature exists just update its value.
def AddOrUpdateSerpFeature(event_type, serp_event_dict, event_value):
    if event_type not in serp_event_dict:
        serp_event_dict[event_type] = 0.0
    serp_event_dict[event_type] += event_value
    return serp_event_dict


def GetRankBucket(visible_elements):
    buckets = []
    for entry in visible_elements.split():
        index = int(entry[entry.rfind('_')+1:])
        if index < 3:
            buckets.append('top')
        elif index < 6:
            buckets.append('middle')
        else:
            buckets.append('bottom')

    return buckets

# merged table is contains first result only. 
def FindMarkovNetwork(merged_table):
    # concat table contains the following: 
    # result table, click table and event table. 
    total_events = 0.0
    vert_markov_trans_prob = {'i':{}, 'v':{}, 'w':{}, 'o':{}}
    vert_markov_trans_sequence = {'i':[], 'v':[], 'w':[], 'o':[]}
    grouped_table = merged_table.groupby(['user_id','task_id'])
    # Find the transition between :
        # start
        # swipe up 
        # swipe down
        # panup and pan down
        # click or click
        # reformulate
        # end
    for name, group in grouped_table:
        group = group.sort('time')
        first_query = False
        task_sequence = []
        first_result_type = None
        last_time = None
        for index, row in group.iterrows():
            # get the first 
            if row['type'] == 'results':
                if not first_query:
                    first_query = True
                    first_result_type = row['doc_type']
                    task_sequence.append('start')
                    last_time = row['time']
                else:
                    #task_sequence.append(GetTimeLabel(row['time'] - last_time))
                    task_sequence.append('reformulate')
                    last_time = row['time']
            # Append the event type. Ignore panleft and right.
            if row['type'] == 'event':
                event_type = row['event_type']
                # Handle double or single tap
                if 'tap' in event_type:
                    #task_sequence.append(GetTimeLabel(row['time'] - last_time))
                    last_time = row['time']
                    task_sequence.append('tap')
                    #if len(row['visible_elements']) > 0:
                        # task_sequence.append('click')
                        #task_sequence.extend(GetRankBucket(row['visible_elements']))
                elif (not first_result_type == 'i') and ('left' in event_type or
                        'right' in event_type):
                    continue
                elif event_type not in ['initial_state','panleft','panright']:
                  if last_time:
                    #task_sequence.append(GetTimeLabel(row['time'] - last_time))
                    last_time = row['time']
                  # replace word pan with swipe
                  event_type = event_type.replace('pan','swipe')
                  task_sequence.append(event_type)
                  #if len(row['visible_elements']) > 0:
                  #    task_sequence.append('click')
                  #    task_sequence.extend(GetRankBucket(row['visible_elements']))
                else:
                    continue
            # append clicks. 
            if row['type'] == 'click':
                #task_sequence.append(GetTimeLabel(row['time'] - last_time))
                last_time = row['time']
                task_sequence.append('click')
        if last_time:
          #task_sequence.append(GetTimeLabel(row['time'] - last_time))
          last_time = row['time']
        task_sequence.append('end')
        if len(task_sequence) > 0 and first_result_type:
            vert_markov_trans_prob=UpdateStateTransitions(task_sequence, first_result_type,\
                vert_markov_trans_prob)
            vert_markov_trans_sequence[first_result_type].append(task_sequence)
            
        else:
            print name, task_sequence, first_result_type

    # Convert into probabilities.
    transition_counts = {}
    for result_type, state_transitions in vert_markov_trans_prob.items():
        total = 0.0
        transition_counts[result_type] = {}
        #for state1 in state_transitions.keys():
        #    total += sum(state_transitions[state1].values())
        print result_type, total
        for state1 in state_transitions.keys():
            transition_counts[result_type][state1] = {}
            total = sum(state_transitions[state1].values())
            for state2 in state_transitions[state1].keys():
                transition_counts[result_type][state1][state2] = vert_markov_trans_prob[result_type][state1][state2]
                vert_markov_trans_prob[result_type][state1][state2] /= total
            print result_type,state1, state_transitions[state1], sum(state_transitions[state1].values())
   
    # Compute the likelihoods. 
    log_likelihoods = {}
    for result_type in transition_counts.keys():
      log_likelihoods[result_type] = ComputeLogLikelihood(\
                                        transition_counts[result_type],\
                                        vert_markov_trans_prob[result_type])
      print result_type, log_likelihoods[result_type]

    # likelihood of each transition matrix with MLE probability
    # estimates of another model. 
    log_likelihood_ratios = {}
    result_types = transition_counts.keys()
    for i in range(len(result_types)):
      for j in range(len(result_types)):
        # Get the transition counts of i and use probabilities of j
        transition_counts_i = transition_counts[result_types[i]]
        transition_probs_j = vert_markov_trans_prob[result_types[j]]
        log_i_j = ComputeLogLikelihood(transition_counts_i, transition_probs_j)
        print result_types[i], result_types[j], log_i_j,\
            log_likelihoods[result_types[i]]
        log_likelihood_ratios[result_types[i]+' '+result_types[j]] =\
                                        log_i_j/log_likelihoods[result_types[i]]
    print log_likelihood_ratios

    # Likelihood of each sequence
    log_likelihood_sequence = {}
    sid = 0
    for i in range(len(result_types)):
      log_likelihood_sequence[result_types[i]] = {}
      # Aggregate counts of each state.
      for sequence in vert_markov_trans_sequence[result_types[i]]:
        log_likelihood_sequence[result_types[i]][sid] = {}
        transition_counts = ComputeTransitionFrequencies(sequence)
        for j in range(len(result_types)):
          # Get the probabilities.
          transition_probabilities = vert_markov_trans_prob[result_types[j]]
          seq_likelihood = ComputeLogLikelihood(transition_counts, transition_probabilities)
          log_likelihood_sequence[result_types[i]][sid][result_types[j]] = seq_likelihood
        sid+=1
    
    # Compute the significance with probabilities. 
    prob_lists = {}
    for result_type in vert_markov_trans_prob.keys():
      prob_lists[result_type] = []
      for state1, state_trans in vert_markov_trans_prob[result_type].items():
        prob_lists[result_type].extend(state_trans.values())
      print  len(prob_lists[result_type])

    for result_type1 in prob_lists.keys():
      for result_type2 in prob_lists.keys():
        print 'wallis ',result_type1,result_type2,\
            kruskalwallis(prob_lists[result_type1],\
            prob_lists[result_type2])

    # Print probabilities per combination for each vertical. 
    transitions = {}
    for result_type in vert_markov_trans_prob.keys():
      for state1, state_trans in vert_markov_trans_prob[result_type].items():
        for state2, value in state_trans.items():
          comb_string = state1+' '+state2
          if comb_string not in transitions:
            transitions[comb_string] = {}
          if result_type not in transitions[comb_string]:
            transitions[comb_string][result_type] = value

    for combination, vert_values in transitions.items():
      print combination, vert_values  

    PlotMarkovTransitions(vert_markov_trans_prob)

def GetTimeLabel(time_diff):
  time_in_sec = time_diff.total_seconds()
  if time_in_sec < 10:
    return 'SI'
  elif time_in_sec < 20:
    return 'MI'
  else:
    return 'LI'
 

def ComputeLogLikelihood(transition_counts, transition_probs):
    # Find the log likelihood of all the models.
    # Find the prob(a|b)^count of (a|b)
    log_likelihood = 0.0
    for state1 in transition_counts.keys():
      for state2, count in transition_counts[state1].items():
        if (state1 in transition_probs) and\
            (state2 in transition_probs[state1]):
          log_likelihood += \
            math.log(transition_probs[state1][state2])*count
        else:
          print state1, state2, 'not present in probabilities.'

    return log_likelihood

def ComputeTransitionFrequencies(task_sequence):
    counts = {}
    prev_state = task_sequence[0]
    for entry in task_sequence[1:]:
        curr_state = entry
        if not (curr_state == prev_state):
            if prev_state not in counts:
                counts[prev_state] = {}
            if curr_state not in counts[prev_state]:
                counts[prev_state][curr_state] = 0.0
            counts[prev_state][curr_state] += 1.0
        prev_state = curr_state
    return counts


def UpdateStateTransitions(task_sequence, result_type, vert_state_trans):
    prev_state = task_sequence[0]
    for entry in task_sequence[1:]:
        curr_state = entry
        if not (curr_state == prev_state):
            if prev_state not in vert_state_trans[result_type]:
                vert_state_trans[result_type][prev_state] = {}
            if curr_state not in vert_state_trans[result_type][prev_state]:
                vert_state_trans[result_type][prev_state][curr_state] = 0.0
            vert_state_trans[result_type][prev_state][curr_state] += 1.0
        prev_state = curr_state
    return vert_state_trans


def FindFirstAndLastClickInfo(concat_table):
    # For each result type: Record time to first click, Record time to last click
    # (Image and video clicks would not have been recorded ! Use taps. 
    '''vertical_stats = {
            'i' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[], 'on_vert_click':0.0,
                   'first_last_same':0.0 }, \
            'v' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[],'on_vert_click':0.0, 'first_last_same':0.0 }, \
            'w' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[], 'on_vert_click':0.0, 'first_last_same':0.0  }, \
            'o' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[] , 'on_vert_click':0.0, 'first_last_same':0.0 }, \
    }
    '''
    vertical_stats = {
            'on' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[], 'on_vert_click':0.0,\
                   'first_last_same':0.0 }, \
            'off' : { 'first_click': [], 'first_rank':[], 'last_click':[],\
                   'last_rank':[], 'total_clicks':0.0, 'off_vert_click':0.0,\
                   'off_vert_rank':[],'on_vert_click':0.0, 'first_last_same':0.0 }
    }

    # Remove task responses.
    concat_table = concat_table[~concat_table['type'].str.contains('task_response')]

    # Group by task_id and query_id and Sort by time within each group.
    grouped_table = concat_table.groupby(['user_id','task_id'])
    for name, group in grouped_table:
        group = group.sort('time')
        vert_type = first_click = first_time = None
        last_time= last_click = result_time = None
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
                    if first_click == last_click:
                        vertical_stats[vert_type]['first_last_same']+=1.0
                    # Set everything to null.
                    first_click= first_time= last_time= last_click=\
                        result_time= vert_type = None
                    recorded_clicks = {}
                # Set vertical type for this page and request time.
                vert_type = str(row['doc_type']).strip()
                if vert_type == row['task_vertical']:
                    vert_type = 'on'
                else:
                    vert_type = 'off'

                result_time = row['time']

            # Found a tap or a click
            start_time  = row['time']
            etype = None
            click_rank = None
            found = False
            if (row['type'] == 'event') and (row['event_type'] == 'tap') and\
                (row['element'] > -1):
                click_url = results[row['element']]['doc_url']
                # check if in clicks.
                if click_url not in recorded_clicks:
                    click_rank = int(row['element'])+1
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
                if click_rank > 10:
                    print row
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

        # Set values for last serp.
        if vert_type and first_click and last_click:
            vertical_stats[vert_type]['first_rank'].append(first_click)
            vertical_stats[vert_type]['last_rank'].append(last_click)
            vertical_stats[vert_type]['first_click'].append(first_time)
            vertical_stats[vert_type]['last_click'].append(last_time)
            if first_click == last_click:
                vertical_stats[vert_type]['first_last_same']+=1.0


    for vertical_type, stats in vertical_stats.items():
        print vertical_type, stats['total_clicks'],\
        'off-click',stats['off_vert_click']/stats['total_clicks'],\
        'on-click',stats['on_vert_click']/stats['total_clicks'],\
        'off-rank',np.mean(stats['off_vert_rank']),np.std(stats['off_vert_rank']),\
        'first-rank',np.mean(stats['first_rank']),np.std(stats['first_rank']),\
        'last-rank',np.mean(stats['last_rank']),np.std(stats['last_rank']),\
        'first-time',np.mean(stats['first_click']),np.std(stats['first_click']),\
        'last-time',np.mean(stats['last_click']),np.std(stats['last_click']),\
        'first_last_same',stats['first_last_same'], (stats['first_last_same']/stats['total_clicks'])

    print 'Man off_vert_rank on-off', kruskalwallis(vertical_stats['on']['off_vert_rank'],vertical_stats['off']['off_vert_rank'])
    print 'Man first_rank  on-off',\
    kruskalwallis(vertical_stats['on']['first_rank'],vertical_stats['off']['first_rank'])
    print 'Man lr on-off',\
    kruskalwallis(vertical_stats['on']['last_rank'],vertical_stats['off']['last_rank'])
    print 'Man fc on-off',\
        kruskalwallis(vertical_stats['on']['first_click'],vertical_stats['off']['first_click'])
    print 'Man lc on-off',\
        kruskalwallis(vertical_stats['on']['last_click'],vertical_stats['off']['last_click'])
    '''
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
    '''
    PlotFirstAndLastClickTime(vertical_stats)
    PlotFirstAndLastClickRank(vertical_stats)
        

def FindDescriptiveStatsPerVertical(concat_table):
    # Find the following stats per vertical:
    # Image Video Wiki : sess, queries, clicks, page-response and
    # task-responses.
    user_stats = {}
    not_registered_clicks = 0.0
    '''
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
    '''
    vertical_stats = {
            'off' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel':[],\
                'page_sat':[], 'task_sat':[] , 'time' : [] }, \
            'on' : {'sess':0.0, 'query': [], 'clicks':[], 'page_rel': [],\
                'page_sat':[], 'task_sat':[], 'time': []}, \
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
                    # To mark on and off vertical.
                    if doc_type == row['task_vertical']:
                        doc_type = 'on'
                    else:
                        doc_type = 'off'

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
    '''print 'Man query i-o', kruskalwallis(vertical_stats['i']['query'],vertical_stats['o']['query'])
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
    '''
    print 'Man query on-off', kruskalwallis(vertical_stats['on']['query'],vertical_stats['off']['query'])
    print 'Man click on-off', kruskalwallis(vertical_stats['on']['clicks'],vertical_stats['off']['clicks'])
    print 'Man page_rel on-off', kruskalwallis(vertical_stats['on']['page_rel'],vertical_stats['off']['page_rel'])
    print 'Man page_sat on-off', kruskalwallis(vertical_stats['on']['page_sat'],vertical_stats['off']['page_sat'])
    print 'Man task sat on-off', kruskalwallis(vertical_stats['on']['task_sat'],vertical_stats['off']['task_sat'])
    print 'Not registered clicks ', not_registered_clicks

def FindTaskSatPerVertical(result_table,task_table):
    # Consider only satisfaction response
    task_table = task_table[task_table['response_type']=='satisfaction']

    # Join on task_table
    merge_table = pd.merge(result_table,task_table,how='right',left_on=['user_id','task_id'],right_on=['user_id','task_id'])
    merge_table.to_csv('merge.csv',encoding='utf-8', index = False)
    
    # satisfaction = {'i':[], 'v':[], 'w':[], 'o':[]}
    satisfaction = {'on':[], 'off':[]}

    for index, row in merge_table.iterrows():
        doc_type = row['doc_type']
        task_vert = row['task_vertical']
        if doc_type == task_vert:
            vert = 'on'
        else:
            vert = 'off'

        # Check if the vertical is a valid vertical
        # Need to check this because not all entires in task db
        # has a corresponding entry in result db
        # These are the people who rated task without executing a single query!
        # We have no choice but to ignore their task ratings
        if vert in satisfaction:
            satisfaction[vert].append(TASKSATMAP[row['response_value']])

    print 'statisfaction',satisfaction
    '''
    print 'image',np.median(satisfaction['i']),np.mean(satisfaction['i']),np.std(satisfaction['i'])
    print 'video',np.median(satisfaction['v']),np.mean(satisfaction['v']),np.std(satisfaction['v'])
    print 'wiki',np.median(satisfaction['w']),np.mean(satisfaction['w']),np.std(satisfaction['w'])
    print 'organic',np.median(satisfaction['o']),np.mean(satisfaction['o']),np.std(satisfaction['o'])
    '''
    print 'on',np.median(satisfaction['on']),np.mean(satisfaction['on']),np.std(satisfaction['on'])
    print 'off',np.median(satisfaction['off']),np.mean(satisfaction['off']),np.std(satisfaction['off'])

    PlotTaskSat(satisfaction)


def FindVerticalPreferenceAndOrientationDistribution(task_table, task_vertical_orientation):
    task_table = task_table[task_table['response_type']=='preferred_verticals']

    
    # Task prefernce per orientation
    task_preference = {'w':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,\
        'Images':0},'v':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,\
        'Images':0},'i':{'Wiki':0,'General Web':0,'Videos':0,'Other':0,\
        'Images':0}}

    for index, row in task_table.iterrows():
        task_orient = task_vertical_orientation[row['task_id']]
        pref_value = row['response_value']
        pref_list = pref_value.split(',')
        for pref in pref_list:
            pref = pref.strip()
            if pref != '':
                task_preference[task_orient][pref] += 1.0

    print task_preference
    for task_orient in task_preference.keys():
        total = sum(task_preference[task_orient].values())
        print task_orient, total
        for key in task_preference[task_orient].keys():
            task_preference[task_orient][key] = float(task_preference[task_orient][key])/total

    for orient, pref in task_preference.items():
        print orient, pref


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

