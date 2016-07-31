import pandas as pd
import numpy as np
import re
from datetime import datetime
import editdistance 
from scipy.stats.mstats import mannwhitneyu, kruskalwallis,ttest_ind
from plotStats import *
import math

from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import roc_curve, auc, confusion_matrix
from scipy import interp
import matplotlib.pyplot as plt


TASKSATMAP = {'Somewhat Satisfied': 2.0, 'Highly Satisfied': 3.0, 'Not Satisfied' : 1.0}

def CorrelationAndClassification(features):
    # write to another file.
    features.to_csv('serp_features_clean.csv',index=False,encoding='utf-8')

    features = features.reset_index()
    # get satisfaction and relevance labels 
    satisfaction = features['satisfaction'].map({1:0,2:0, 3:0, 4:1,5:1 })
    print satisfaction.value_counts()
    print satisfaction.shape
    relevance = features['relevance']

    # take every column and find 
    # set all other values to 0. 
    remaining_features = features.drop(['relevance','satisfaction',\
            'first_event_time','first_result_time','query_task'], axis =1)
    # Merge the features : (tap and double tap)
    remaining_features =  remaining_features.drop(['index','tap_distance'], axis = 1)
    remaining_features = remaining_features.fillna(0)

    # map the vertical name to number.
    remaining_features['result_type'] =\
            remaining_features['result_type'].map({'i':1, 'v':2, 'w':3, 'o':4})
    

    # Normalize the features
    remaining_features = (remaining_features - remaining_features.mean()) \
            / (remaining_features.max() - remaining_features.min())
    # Convert the features into lists. 
    features_list = remaining_features.values.tolist()
   
    for c in [1,2]:
        mean_tpr = 0.0
        mean_fpr = np.linspace(0, 1, 100)
        all_tpr = []
        confusion_matrix_total = {}
        # Predict Satisfaction using Logistic regression and print auc.
        for k, (train, test) in enumerate(StratifiedKFold(satisfaction, 5)):
            x_train = [ features_list[i] for i in train]
            y_train = satisfaction.loc[train]
            x_test = [ features_list[i] for i in test]
            y_test = satisfaction[test]
            clf = LogisticRegression(C=c, penalty='l1')
            clf_fit = clf.fit(x_train, y_train)
            coeff = clf_fit.coef_.ravel()
            coeff_tuple = []
            for i in range(len(list(remaining_features.columns))):
                coeff_tuple.append((remaining_features.columns[i],round(coeff[i],5)))
            print 'k=',k,'c=',c
            for ctuple in coeff_tuple:
                print ctuple[0], ctuple[1]
            # Get the confusion matrices. 
            y_predict= clf_fit.predict(x_test)
            confusion_fold = confusion_matrix(y_test, y_predict)
            for i in range(len(confusion_fold)):
                total = sum(confusion_fold[i])
                if i not in confusion_matrix_total:
                    confusion_matrix_total[i] = {}
                for j in range(len(confusion_fold)):
                    if j not in confusion_matrix_total[i]:
                        confusion_matrix_total[i][j] = 0.0
                    confusion_matrix_total[i][j] += (confusion_fold[i][j] *1.0)/total 
            
            prob_y_test = clf_fit.predict_proba(x_test)
            fpr, tpr, thresholds = roc_curve(y_test, prob_y_test[:, 1])
            mean_tpr += interp(mean_fpr, fpr, tpr)
            mean_tpr[0] = 0.0
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (k,
                roc_auc))

        for i, jdict in confusion_matrix_total.items():
            for j,value in jdict.items():
                print 'logistic c=',c,i,j,value/5


        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
        mean_tpr /= 5  # Number of folds. 
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        plt.plot(mean_fpr, mean_tpr, 'k--',
                         label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic Logistic C='+str(c))
        #plt.legend(loc="lower right")
        plt.legend(loc='lower right', ncol = 1, fontsize=15)
        plt.savefig('roc_logistic_'+str(c)+'.png',bbox_inches='tight')
        plt.show()
        #plt.clf()

def ComputeSERPFeatures(merged_table):
    grouped_table = merged_table.groupby(['user_id','task_id'])
    query_regex = re.compile('query=(.*?)(&|\Z)')
    # Find the correlation between the following and satisfaction :
        # count of gestures. 
        # reformulation
        # number of clicked results
        # total time on SERP
        # Last depth viewed before first click.
        # first clicked rank.
        # distance of all swipe gestures
        # time to first click  
        # screen time of first 3 results, 3-6 results and bottom results. 
    
    # Serp level response does not contain the result type on type. 
    # thus tie it to the query. 
    serp_score_and_features = {}
    for name, group in grouped_table:
        group = group.sort('time')
        query_result_type_string = None
        curr_time = None
        for index, row in group.iterrows():
            curr_time = row['time']
            if row['type'] == 'results':
                # Update the previous query and type features with
                # reformulation.
                if query_result_type_string:
                    serp_score_and_features[query_result_type_string]['reformulate']= 1.0
                # Initialize the key. 
                first_result_type = row['doc_type']
                query =  row['query_text']
                query_result_type_string = first_result_type+'_'+\
                                            query.replace(' ','_')+'_'+\
                                            row['user_id']+'_'+str(row['task_id'])
                if query_result_type_string not in serp_score_and_features:
                    serp_score_and_features[query_result_type_string] = {}
                # Add the number of terms in query as feature. 
                serp_score_and_features[query_result_type_string] = SetSerpFeature(\
                        'query_term_count',serp_score_and_features[query_result_type_string],\
                        len(query.split()))
                serp_score_and_features[query_result_type_string] = SetSerpFeature(\
                        'first_result_time',serp_score_and_features[query_result_type_string],\
                        row['time'])

            if query_result_type_string:
                if row['type'] == 'event':
                    # Set last event time. 
                    if 'last_event_time' in\
                        serp_score_and_features[query_result_type_string]:
                        serp_score_and_features[query_result_type_string]['last_event_time']=\
                            max(serp_score_and_features[query_result_type_string]['last_event_time'],row['time'])
                    else:
                        serp_score_and_features[query_result_type_string]['last_event_time']=row['time']

                    # Add first event time. 
                    event_type = row['event_type']
                    # Remove pan and double events. 
                    if 'pan' in event_type:
                      event_type = event_type.replace('pan','swipe')
                    if 'double' in event_type:
                      event_type = event_type.replace('double','')

                    serp_score_and_features[query_result_type_string] = SetSerpFeature(\
                            'first_event_time',serp_score_and_features[query_result_type_string],\
                            row['time'])
                    # Add event counts. 
                    if ('tap' in event_type) or ('pan' in event_type) or ('swipe'\
                            in event_type):
                        # Add first event time.
                        serp_score_and_features[query_result_type_string]=SetSerpFeature(\
                            'first_'+event_type+'_time',\
                            serp_score_and_features[query_result_type_string],\
                            row['time'])

                        # Update the event count. 
                        serp_score_and_features[query_result_type_string] =\
                          IncrementSerpFeature(event_type+'_count',\
                          serp_score_and_features[query_result_type_string],1.0)

                        # Update the distance total. 
                        serp_score_and_features[query_result_type_string] =\
                          IncrementSerpFeature(event_type+'_distance',\
                          serp_score_and_features[query_result_type_string],\
                          row['distance'])

                        # Record the time of event. 
                        serp_score_and_features[query_result_type_string] =\
                          AppendValueToSERPFeature('time_list_'+event_type,\
                          serp_score_and_features[query_result_type_string],\
                          row['time'])


                        # Add pre-click information 
                        if ('first_click_time' not in \
                            serp_score_and_features[query_result_type_string]) and \
                            ('first_tap_time' not in\
                            serp_score_and_features[query_result_type_string]):

                            # Update the event count. 
                            serp_score_and_features[query_result_type_string] =\
                                    IncrementSerpFeature('pre_click_'+event_type+'_count',\
                                    serp_score_and_features[query_result_type_string],1.0)

                            # Update the distance total. 
                            serp_score_and_features[query_result_type_string] =\
                                    IncrementSerpFeature('pre_click_'+event_type+'_distance',\
                                    serp_score_and_features[query_result_type_string],\
                                    row['distance'])
                            # Record the time of event. 
                            serp_score_and_features[query_result_type_string] =\
                              AppendValueToSERPFeature('pre_click_time_list_'+event_type,\
                              serp_score_and_features[query_result_type_string],\
                              row['time'])


                    # Add visibility of results
                    visible_positions_list=GetVisibleRanks(row['visible_elements']) 
                    if len(visible_positions_list) > 0: 
                        # Update the last visible position and time before first click.
                        if 'first_click_time' not in \
                                serp_score_and_features[query_result_type_string]:
                            # Add the last position. This has to be updated with each
                            # row. Thus cant use SetSerpFeature function. 
                            serp_score_and_features[query_result_type_string]\
                                    ['last_visible_result_before_click']=\
                                    max(visible_positions_list)
                        
                        # Add time of visibility for each element on SERP.
                        # (Not very correlated)
                        # for visible_element in visible_positions_list:
                        #    serp_score_and_features[query_result_type_string]=\
                        #        IncrementSerpFeature(str(visible_element)+'_viewport_ms', \
                        #        serp_score_and_features[query_result_type_string],\
                        #        row['delta_time'])
                        
                        # Update the rank of last visible result for the whole serp
                        # time.
                        serp_score_and_features[query_result_type_string]['last_visible_result']=\
                            max(visible_positions_list)

                    # Update the bucket count. The results are (top, med and bottom
                    # buckets)
                    for result_bucket in GetRankBucket(row['visible_elements']):
                        serp_score_and_features[query_result_type_string]=\
                            IncrementSerpFeature(result_bucket+'_count', \
                            serp_score_and_features[query_result_type_string],\
                            1.0)
                        serp_score_and_features[query_result_type_string]=\
                            IncrementSerpFeature(result_bucket+'_viewport_ms', \
                            serp_score_and_features[query_result_type_string],\
                            row['delta_time'])

                # Add click info. 
                if row['type'] == 'click':
                    # Add the first click time.
                    serp_score_and_features[query_result_type_string]=SetSerpFeature(\
                            'first_click_time',\
                            serp_score_and_features[query_result_type_string],\
                            row['time'])
                    # Update the click count. 
                    serp_score_and_features[query_result_type_string] =\
                            IncrementSerpFeature('click_count',\
                            serp_score_and_features[query_result_type_string],1.0)
                    # Update rank.
                    serp_score_and_features[query_result_type_string]=SetSerpFeature(\
                            'first_click_rank',\
                            serp_score_and_features[query_result_type_string],\
                            int(row['doc_id'][row['doc_id'].find('_')+1:])+1)
                  
                    # Record the click rank 
                    serp_score_and_features[query_result_type_string] =\
                      AppendValueToSERPFeature('click_rank_list',\
                      serp_score_and_features[query_result_type_string],\
                      int(row['doc_id'][row['doc_id'].find('_')+1:])+1)
                
                # Record the satisfaction and relevance for SERP response. 
                if row['type'] == 'page_response' and\
                        '128.16.12.66:4730/' in row['doc_url']:
                    # Get the query, task-id and user-id
                    variable = re.search(query_regex,row['doc_url'])
                    query = ''
                    if variable:
                        query = variable.group(1)
                    # Since we dont know which vertical-query it is, search through
                    # all keys. 
                    if len(query) > 0:
                        query = query.replace('+','_')
                        key = query+'_'+row['user_id']+'_'+str(row['task_id'])
                        for entry in serp_score_and_features.keys():
                            if key in entry:
                                serp_score_and_features[entry][row['response_type']]=\
                                        row['response_value']
                                # Set last event time. 
                                if 'last_event_time' in\
                                    serp_score_and_features[query_result_type_string]:
                                        serp_score_and_features[query_result_type_string]['last_event_time']=\
                                        max(serp_score_and_features[query_result_type_string]['last_event_time'],row['time'])
                                else:
                                    serp_score_and_features[query_result_type_string]['last_event_time']=row['time']
        # Update the data for last serp in group. 
        if query_result_type_string:
            if 'last_event_time' not in\
                serp_score_and_features[query_result_type_string]:
                    serp_score_and_features[query_result_type_string]=\
                       SetSerpFeature('last_event_time',\
                       serp_score_and_features[query_result_type_string],\
                       curr_time)

    # Use the dictionary to create training data.
    serp_feat_list = []
    for key, feat_dict in serp_score_and_features.items():
        feat_dict['query_task'] = key[key.find('_')+1:]
        feat_dict['result_type'] = key[:key.find('_')]
        # get the time differences in second and delete the timestamps. 
        first_time = None
        if 'first_event_time' in feat_dict :
            first_time = feat_dict['first_event_time']
        else:
            first_time = feat_dict['first_result_time']
        for feat_key in feat_dict.keys(): 
            # List of times. Get the average instead. 
            if 'time_list' in feat_key:
                feat_dict[feat_key] = GetAverageBetweenTwoEntries(feat_dict[feat_key])
            elif 'time' in feat_key:
                feat_dict[feat_key] = (feat_dict[feat_key] - first_time)\
                        .total_seconds()
            if 'rank_list' in feat_key:
                print feat_dict[feat_key] 
                feat_dict[feat_key] = np.mean(feat_dict[feat_key])

        for feat_key in feat_dict.keys():  
            if 'viewport_ms' in feat_key:
                # Convert ms into seconds and then convert into ratio.  
                feat_dict[feat_key] =  (feat_dict[feat_key]*0.001)

        serp_feat_list.append(feat_dict)

    serp_feature_frame = pd.DataFrame.from_dict(serp_feat_list)
    filtered_feature_frame = serp_feature_frame[\
                    ~(serp_feature_frame['relevance'].isnull() |\
                    serp_feature_frame['relevance'].isnull())]
    filtered_feature_frame = filtered_feature_frame[\
            filtered_feature_frame['last_event_time'] < 500.0]
   
    '''
    PlotSatAndRelBoxPlotPerVertical(filtered_feature_frame.groupby('result_type'),\
                                    'SERP Response',\
                                    'rel_sat_serp_resonse.png')
    '''
    return filtered_feature_frame

def GetAverageBetweenTwoEntries(time_list):
  difference = []
  for i in range(len(time_list)-1):
    j = i+1
    difference.append((time_list[j] - time_list[i]).total_seconds())
  
  if len(difference) > 0:
    return max(difference)
  return 0


# Feature is a list of values (mostly times, ranks etc). Append a value to 
# list. 
def AppendValueToSERPFeature(event_type, serp_event_dict, event_value):
    if event_type not in serp_event_dict:
        serp_event_dict[event_type] = []
    if (len(serp_event_dict[event_type]) == 0) or \
      (serp_event_dict[event_type][-1] != event_value):
        serp_event_dict[event_type].append(event_value)
        
    return serp_event_dict

# Add a feature to serp only if it does not exist. Useful to add time oriented
# features such as first click/event/tap time. 
def SetSerpFeature(event_type, serp_event_dict, event_value):
    if event_type not in serp_event_dict:
        serp_event_dict[event_type] = event_value
    return serp_event_dict

# If the feature exists just update its value.
def IncrementSerpFeature(event_type, serp_event_dict, event_value):
    if event_type not in serp_event_dict:
        serp_event_dict[event_type] = 0.0
    serp_event_dict[event_type] += event_value
    return serp_event_dict

def GetVisibleRanks(visible_string):
    indices = []
    for entry in visible_string.split():
        index = int(entry[entry.rfind('_')+1:])
        indices.append(index+1)
    return indices

def GetRankBucket(visible_elements):
    buckets = []
    for entry in visible_elements.split():
        index = int(entry[entry.rfind('_')+1:])
        if index == 0:
            buckets.append('firstr')
        if index < 4:
            buckets.append('top')
        elif index < 7:
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
                if vert_type and first_click > -1 and last_click > -1:
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

                if first_click > -1:
                    first_time  = (start_time - result_time).total_seconds()
                    if (first_time < 50):
                        first_click = click_rank
                last_click = click_rank
                last_time = (start_time - result_time ).total_seconds()
                # Set everything to null
                etype = None
                found = False

        # Set values for last serp.
        if vert_type and first_click > -1 and last_click > -1:
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

    verticals = vertical_stats.keys()
    for i in range(len(verticals)):
        v1 = verticals[i]
        for j in range(i+1,len(verticals)):
            v2 = verticals[j]
            for attribute in ['off_vert_rank','first_rank',\
                    'last_rank','first_click','last_click']:
                print 'Man off_vert_rank ',v1, v2,attribute,\
                    kruskalwallis(vertical_stats[v1][attribute],vertical_stats[v2][attribute])
    
    PlotFirstAndLastClickTime(vertical_stats)
    PlotFirstAndLastClickRank(vertical_stats, 'Examined Result Pos', 'Result Rank',\
                    '','first_and_last_click_rank.png') 

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
    verticals = vertical_stats.keys()
    for i in range(len(verticals)):
        v1 = verticals[i]
        for j in range(i+1,len(verticals)):
            v2 = verticals[j]
            for attribute in ['query','clicks','page_rel',\
                    'page_sat','task_sat']:
                print 'Man query',v1,v2,attribute,\
                        kruskalwallis(vertical_stats[v1][attribute],\
                        vertical_stats[v2][attribute])
    
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

