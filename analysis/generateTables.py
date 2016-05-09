import argparse
import pandas as pd
import numpy as np
import json
import re

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

# TODO:
# Remove repeated clicks for the same document

# Query pattern to extract from server url.
query_id_pattern = 'queryid=(.*?)&'
query_id_regex = re.compile(query_id_pattern)

# Query pattern to extract from server url.
page_id_pattern = 'page=(.*?)&'
page_id_regex = re.compile(page_id_pattern)

# Query pattern to extract from server url.
docurl_pattern = 'docurl=(.*)'
docurl_regex = re.compile(docurl_pattern)


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

def ReadDB(event_file):
    event_db = json.load(event_file)
    return event_db

def FormatUrl(url):
    # Just remove the last char /
    if url[-1] == '/':
        url = url[: -1]
    if url.find('http://') == 0:
        url = url[7:]
    if url.find('https://') == 0:
        url = url[8:]

    return url

# TODO
# Some doc_url does not have queryid and pageid (e.g., https://m.youtube.com/watch?v=RZ_YOAlPJNY)
# We use empty strings if we do not find any match
def BreakServerUrl(url):
	query_id = re.search(query_id_regex,url)
	if not query_id:
		query_id = -1
	else:
		query_id = query_id.group(1)

	page_id = re.search(page_id_regex, url)
	if not page_id:
		page_id = -1
	else:
		page_id = page_id.group(1)

	doc_url = re.search(docurl_regex,url)
	if not doc_url:
		doc_url = url
	else:
		doc_url = doc_url.group(1)

	return query_id, page_id, FormatUrl(doc_url)

'''
Convert an array of databases to a tsv. 
@databases can be an array of Json objects.
@columns is the column header to assign to pandas object.

'''
def FormatPageResponseDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
	    # Format of Page Response db
	    # "time_stamp":{"user_id":"marzipan","task_id":"8",
	    # "doc_url":"page=1&docid=aid_2&queryid=0&user=marzipan&task=8&docurl=url",
	    # "response_type":"relevance","response_value":"5.0"},
	    query_id, page_id, doc_url = BreakServerUrl(values['doc_url'])
	    new_entry = [entry , values['user_id'] , int(values['task_id']),\
		int(query_id), int(page_id), doc_url, values['response_type'], \
                values['response_value']]
	    tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    # Remove duplicate rows
    return tsv_frame.drop_duplicates()

def FormatTaskResponseDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
	    # Format of Task Response db
	    # "time_stamp":{"user_id":"marzipan","task_id":"8",
	    # "response_type":"preferred_verticals",
	    # "response_value":"Images , Wiki , General Web"}
	    new_entry = [entry , values['user_id'] , int(values['task_id']),\
                values['response_type'],values['response_value']]
	    tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    return tsv_frame.drop_duplicates()

def FormatQueryResultDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            # Format of Query Result db
            # "time_stamp":{"user_id":"","query_id":4,"task_id":"4","query_text":"","page_id":1,"search_results":[["i",[{"title":"","external_url":"","display_url":"","thumbnail":""},{"title":"","external_url":"","display_url":"","thumbnail":""}...]],["o",{"title":"","desc":"","display_url":"","external_url":""}],["o",{"title":"","desc":"","display_url":"","external_url":""}]...]}
            search_results = values['search_results']

            # The documents are stored in the order in which
            # they are displayed on the search results page.
            doc_pos = 0
            for result in search_results:
                doc_type = result[0]

                # All verticals have only one result except image
                # In case of image vertical we show multiple images
                # so pick the first image and ignore the rest
                if (doc_type == 'i'):
                    doc_prop = result[1][0]
                else:
                    doc_prop = result[1]

                doc_title = doc_prop['title']
                doc_url = FormatUrl(doc_prop['external_url'])
                new_entry = [entry , values['user_id'] , int(values['task_id']),\
                    int(values['query_id']), values['query_text'], int(values['page_id']), \
                    doc_pos, doc_type, doc_title, doc_url]
                tsv_data.append(new_entry)

                # Document position starts with zero
                doc_pos = doc_pos + 1
    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)
    return tsv_frame.drop_duplicates()

def FormatClickResultDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            # Format of Click Result db
            #{"time_stamp":{"user_id":"marzipan","query_id":"0",
            #"page_id":"1","task_id":"8","doc_id":"aid_1",
            #"doc_url":"http://www.theplunge.com/bachelorparty/bachelor-party-ideas-2/"}
            new_entry = [entry , values['user_id'] , int(values['task_id']),\
                    int(values['query_id']),int(values['page_id']), \
                    values['doc_id'],FormatUrl(values['doc_url'])]
            tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    return tsv_frame.drop_duplicates()


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
    page_response_db = []
    task_response_db = []
    query_result_db = []
    click_result_db = []

    # If a single event and response db file
    if not arg.isFolder:
        p_db = ReadDB(open(arg.pageResponseDB,'r'))
        page_response_db.append(p_db)

        t_db = ReadDB(open(arg.taskResponseDB,'r'))
        task_response_db.append(t_db)

        q_db = ReadDB(open(arg.queryResultDB,'r'))
        query_result_db.append(q_db)

        c_db = ReadDB(open(arg.clickResultDB,'r'))
        click_result_db.append(c_db)
    else:
        for pfile in os.listdir(arg.pageResponseDB):
            p_db = ReadDB(open(arg.pageResponseDB+'/'+pfile,'r'))
            page_response_db.append(p_db)
        
        for tfile in os.listdir(arg.taskResponseDB):
            t_db = ReadDB(open(arg.taskResponseDB+'/'+tfile,'r'))
            task_response_db.append(t_db)

        for qfile in os.listdir(arg.queryResultDB):
            q_db = ReadDB(open(arg.queryResultDB+'/'+qfile,'r'))
            query_result_db.append(q_db)

        for cfile in os.listdir(arg.clickResultDB):
            c_db = ReadDB(open(arg.clickResultDB+'/'+cfile,'r'))
            click_result_db.append(c_db)            

    # Format page response db
    page_response_table = FormatPageResponseDB(page_response_db, page_response_header, page_reponse_sortkeys)
    
    # Format task response db
    task_response_table = FormatTaskResponseDB(task_response_db,task_response_header,task_response_sortkeys)

    # Format query result db
    query_result_table = FormatQueryResultDB(query_result_db,query_result_header,query_result_sortkeys)
    #query_result_table.to_csv('query_result_table.csv', index = False,\
    #        encoding='utf-8', sep='\t');
    
    # Format click result db
    click_result_table = FormatClickResultDB(click_result_db,click_result_header,click_result_sortkeys)
    

    # Remove test users
    page_response_table = page_response_table[~page_response_table['user_id'].str.contains('test')]
    task_response_table = task_response_table[~task_response_table['user_id'].str.contains('test')]
    query_result_table = query_result_table[~query_result_table['user_id'].str.contains('test')]
    click_result_table = click_result_table[~click_result_table['user_id'].str.contains('test')]

    # a. task : users. Compute the number of users who provided task feedback
    # task_id, #users_who_gave_feedback
    task_response_table[['task_id','user_id']].groupby(['task_id']).\
            agg({'user_id':pd.Series.nunique}).to_csv('task_feedback.csv')

    # b. task : user_impressions. Compute the number of users who executed a task.
    # task_id, #users_who_executed_task
    page_response_table[['task_id','user_id']].groupby(['task_id']).\
            agg({'user_id':pd.Series.nunique}).to_csv('task_execute.csv')

    # c. task : vertical_views. Compute the number of times each vertical was shown as top result. 
    # Only consider query results in the first page (page_id==1)
    # Here we output counts for all the doc position in the first page
    # task_id, doc_type, doc_pos, #occurances
    query_results = query_result_table[query_result_table['page_id']==1]
    query_results[['task_id','doc_type','doc_pos']].groupby(\
            ['task_id','doc_type','doc_pos']).\
            count().to_csv('vertical_pos.csv')

    # d. task : queries. Compute the number of queries fired for the task.
    # task_id, #unique_queries
    queries_with_time= query_result_table[\
            ['time','task_id','query_text']].drop_duplicates();
    
    queries_with_time.groupby(['task_id','query_text']).agg(\
            {'query_text':pd.Series.count}).to_csv('task_queries.csv')

    # e. task : clicks. Compute the number of clicks for the task. 
    # task_id, click_url, #clicks
    click_result_table[['task_id','doc_url']].groupby(['task_id','doc_url']).\
            count().to_csv('task_clicks.csv',encoding='utf-8',sep='\t')

    # f. task : time . Compute the time spent on doing each task.

    # g. task : click_ranks. Compute the number of times a position was clicked
    # ignore positions with double digits as they are nested clicks
    # doc_pos = (page_id - 1) * 10 + doc_id
    # task_id, doc_pos, #clicks
    click_filtered = click_result_table[click_result_table['doc_id'].str.len()\
            == 5]
    click_filtered['doc_pos'] = (click_filtered['page_id'].astype(float) -\
            1.0) + (click_filtered['doc_id'].str[4]).astype(float)    
    # Filter the columns for count.
    click_filtered[['task_id','doc_pos']].groupby(['task_id','doc_pos'])['doc_pos'].\
            count().to_csv('task_rank_click_counts.csv', encoding = 'utf-8',\
            sep = '\t')

    # h. task : time_to_first_click. Compute the time to first click for each
    # task. Compute mean and standard deviation. 
    # Replace multiple columns with one. 

    # Merge click and results.
    query_result_table['doc_url'] = query_result_table['doc_url'].str.strip();
    mod_click = click_result_table.groupby(['user_id', 'task_id',\
        'query_id','page_id', 'doc_id' ,\
        'doc_url']).min().reset_index().sort('time')
    mod_click['doc_url'] = mod_click['doc_url'].str.strip();

    merged_result_and_click = pd.merge(query_result_table[['time','user_id','task_id',\
            'query_id','page_id', 'doc_url','doc_pos','doc_type']],mod_click, \
            left_on = ['user_id','task_id','query_id','page_id', 'doc_url'], \
            right_on =['user_id','task_id','query_id','page_id', 'doc_url'])

    # Take the time difference of times.  
    merged_result_and_click['time_diff']= merged_result_and_click['time_y']-\
            merged_result_and_click['time_x']

    # j. task : first_click_position. Compute the list of ranks that were clicked first for task. 
    # task_id, doc_pos, #first_clicks

    # k. task : last_click_position. Compute the ranks that were clicked last for
    # each task. 
    # task_id, doc_pos, #last_clicks

if __name__ == "__main__":
    main()
