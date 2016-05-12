
# Cant use this anymore since there was an error in click logging :(
def FindTimeToFirstClick(click_table, result_table):

    # Find the first-result type for each tuple (query_id, task_id, user_id,
    # page_id)
    first_result_type =  result_table[result_table['doc_pos'] == 0]
    first_result_type = first_result_type[['query_id','user_id','task_id',\
            'page_id', 'doc_pos','doc_type']]

    # Merge click and results. Will filter clicks whose origin was not serp. 
    result_table['doc_url'] = result_table['doc_url'].str.strip();
    click_table['doc_url'] = click_table['doc_url'].str.strip();

    merged_result_and_click = pd.merge(result_table[['time','user_id','task_id',\
            'query_id','page_id', 'doc_url','doc_pos','doc_type',]],click_table, \
            left_on = ['user_id','task_id','query_id','page_id', 'doc_url'], \
            right_on =['user_id','task_id','query_id','page_id', 'doc_url'])

    # Take the time difference of times.  
    merged_result_and_click['time_x'] =  pd.to_datetime(merged_result_and_click['time_x'],unit='s')
    merged_result_and_click['time_y'] =  pd.to_datetime(merged_result_and_click['time_y'],unit='s')

    merged_result_and_click['time_diff']= merged_result_and_click['time_y']-\
            merged_result_and_click['time_x']

    # Drop the times 
    merged_result_and_click = merged_result_and_click.drop(['time_x'], axis = 1)

    # Take the intersection.
    all_clicks_with_result_type = pd.merge(merged_result_and_click,\
            first_result_type, left_on = ['user_id','task_id','query_id',\
            'page_id'], right_on = ['user_id','task_id','query_id',\
            'page_id'])

    # sort by time, task-id, user-id and query-id
    all_clicks_with_result_type = all_clicks_with_result_type.sort(\
            ['time_y','user_id','task_id','query_id']);
    all_clicks_with_result_type.to_csv('all_clicks_with_result_type.csv',
            encoding = 'utf-8', sep = '\t', index = False)

    # Just select the first and last entry for each combination (task_id,
    # query_id, user_id, and page_id)
