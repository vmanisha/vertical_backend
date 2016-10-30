import argparse
import pandas as pd
import numpy as np
import json
import os
import re
from datetime import datetime
from formatTables import *
from computePageLevelMetrics import *
from computeVerticalLevelMetrics import *
from computeEventStats import *
from classification import *
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

# Visibility event table header
# event_value is visible doc_id
scroll_event_header =['time','user_id','task_id','query_text','event_type',\
                      'event_value','visible_elements','event_dist',
                      'direction','page_height', 'event_x','event_y' ]
# Visibility event table sortkeys
scroll_event_sortkeys = [ 'user_id','task_id', 'time']

# All event table 
all_event_header =['time','user_id','task_id','query_text','page_id','event_type',\
                      'element','direction','distance','delta_time', 'visible_elements']
# Visibility event table sortkeys
all_event_sortkeys = [ 'user_id','task_id', 'time']



def MergeAllTables(result_table, click_table, event_table, page_table, task_table):
    result_table['type'] = 'results'
    click_table['type'] = 'click'
    page_table['type'] = 'page_response'
    task_table['type'] = 'task_response'
    event_table['type'] = 'event'

    # Concatinate all tables. Keep only the first result.
    # values not present will be N/A
    # result_first = result_table[result_table['doc_pos'] == 0]
    concat_table = pd.concat([result_table, click_table,event_table, page_table,\
        task_table], ignore_index = True)
    concat_table.to_csv('concat_tables.csv', index = False, encoding = 'utf-8')
    return concat_table

def AssignTaskVerticalLabel(results_table, task_dict):
  results_table['task_vertical'] = None
  for task_id, task_vert in task_dict.items():
    # Get all the rows with task_id.
    # assign task vertical from dictionary.
    results_table.loc[(results_table['task_id'] == task_id),'task_vertical'] = task_vert
  return results_table

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

    # Format event db
    all_event_table = FormatAllEventDB(event_db, all_event_header, all_event_sortkeys)
    
    # a. task : users. Compute the number of users who provided task feedback
    # task_id, #users_who_gave_feedback
    # task_response_table[['task_id','user_id']].groupby(['task_id']).\
    #        agg({'user_id': pd.Series.nunique}).to_csv('task_feedback.csv')

    # b. task : user_impressions. Compute the number of users who executed a task.
    # task_id, #users_who_executed_task
    # page_response_table[['task_id','user_id']].groupby(['task_id']).\
    #         agg({'user_id': pd.Series.nunique}).to_csv('task_execute.csv')

    # c. vertical_type : vertical_SERPs. Compute the number of times each vertical was shown as top result.
    # Only consider query results in the first page (page_id==1)
    # Here we output counts for all the doc position in the first page
    # doc_type, #occurances
    # query_results = query_table[(query_table['page_id']==1) & \
    #        (query_table['doc_pos'] == 0)]
    # print query_results.groupby(['doc_type'])['task_id'].count()

    # d. vertical_type : queries. Compute the number of queries fired for each vertical.
    # task_id, #unique_queries
    # queries_with_time= query_results[['time','doc_type','query_text']].drop_duplicates();
    # queries_with_time.groupby(['doc_type','query_text']).agg(\
    #        {'query_text': pd.Series.count}).to_csv('vert_queries.csv')

    # g. task : click_ranks. Compute the number of times a position was clicked
    # ignore positions with double digits as they are nested clicks
    # task_id, doc_pos, #clicks
    click_filtered = click_table[click_table['doc_id'].str.len()\
            == 5]

    # query_filtered = query_table[query_table['doc_pos'] == 0]
    
    # Filter the columns for count.
    #click_filtered[['task_id','doc_pos']].groupby(['task_id','doc_pos'])['doc_pos'].\
    #        count().to_csv('task_rank_click_counts.csv', encoding = 'utf-8',\
    #        sep = '\t')
    print 'Page Rel ', page_response_table[page_response_table['response_type'] == 'relevance']['response_type'].value_counts()
    print 'Page Sat ', page_response_table[page_response_table['response_type'] ==\
        'satisfaction']['response_type'].value_counts()
    print 'Task Sat ', task_response_table[task_response_table['response_type']
        == 'satisfaction']['response_type'].value_counts()
    print 'Task Sat ', task_response_table[task_response_table['response_type'] ==
        'satisfaction'].count()

    # Concatenate event, pageresponse, task_response, click, result tables.
    # Fix the gaps. And complete all columns and save them. 
    # Format tap event db
    # tap_event_table = FormatEventDBForTap(event_db,tap_event_header,tap_event_sortkeys)
    # Assign the on-off vertical label depending on tasktype. 
    task_vert_dict = {1:'i',2:'i',3:'w',4:'w',5:'v',6:'w',7:'w',8:'v',9:'i',10:'v'}
    results_with_task_type = AssignTaskVerticalLabel(query_table,\
        task_vert_dict)

    merged_tables = MergeAllTables(results_with_task_type, click_filtered, all_event_table,\
    	 page_response_table, task_response_table)
    # Find the scroll distribution before time to first click.
    # ComputeScrollDistributionBeforeClick(merged_tables)
    # Find state transitions. 
    # FindMarkovNetwork(merged_tables)

    # Serp features. 
    # serp_features = ComputeSERPFeatures(merged_tables)
    # remaining_features, satisfaction = PrepareFeaturesAndSatisfactionLabels(serp_features,'serp_features_clean.csv')
    # Get classification results
    # PerformClassificationViaCrossValidation(remaining_features, satisfaction,'classifier.csv')
    # Compute Mean and std-dev of features for SAT and DSAT labels. 
    # ComputeFeatMeanStdDevOfSatAndDSatLabels(remaining_features) 

    # ComputePreClickDistributions(merged_tables)

    # Filter query table to have only top position on first page
    # TODO: Do this after merge tables as it adds 'type' which is used later
    
    # # Find the vertical_type stats: sessions, queries, clicks a
    # # nd average satisfaction/rel values.
    # FindDescriptiveStatsPerVertical(merged_tables)
    
    # # h. vertical_type : time_to_first_click_and_position. Compute the time to first click for each
    # # k. vertical_type : last_click_position. Compute the ranks that were clicked last for
    # FindFirstAndLastClickInfo(merged_tables)
    
    # # For every page whose response is available find its doc_pos on serp
    # # We ignore the pages who are serp since they do not have any doc_pos
    # FindPageMetricsPerVertical(query_table,page_response_table)

    # # Find dwell time information for each vertical for on-vert and off-vert
    # # click. 
    FindDwellTimes(merged_tables)

    # # Generate visibility statistics
    # Format visibility event db
    # vis_event_table = FormatEventDBForVisibility(event_db,vis_event_header,vis_event_sortkeys)
    # FindVisiblityMetricsPerVertical(query_filtered,vis_event_table)

    # # Generate task statisfaction stats per vertical
    # FindTaskSatPerVertical(results_with_task_type,task_response_table)

    # # Generate task preference stats per vertical
    # FindTaskPrefPerVertical(query_filtered,task_response_table)

    # # Generate task preference distribution per task_id
    # FindTaskPrefDistribution(task_response_table, task_vert_dict)
    # FindVerticalPreferenceAndOrientationDistribution(task_response_table, task_vert_dict)
    
    # # Generate click distribution for every vertical
    # # FindClickDistributionPerVertical(query_filtered,click_filtered)

    # Format scroll event db
    #scroll_event_table = FormatEventDBForScrolls(event_db,scroll_event_header,\
    #    scroll_event_sortkeys)
    # # Find Scroll event stats
    #FindPageScrollDistributionPerVertical(query_table, scroll_event_table)

    # Find time-scroll freq ratio
    #FindPageVelocityDistribution(query_table, all_event_table)

if __name__ == "__main__":
    main()
