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
#   g. task : click_ranks. Compute the number of times a document was clicked
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
# remove test users

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


def ReadDB(event_file):
    event_db = json.load(event_file)
    return event_db

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
		doc_url = ""
	else:
		doc_url = doc_url.group(1)

	return query_id, page_id, doc_url


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
				int(query_id), int(page_id), doc_url,
                values['response_type'], \
                values['response_value']]
			tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    return tsv_frame 

def FormatTaskResponseDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
			# Format of Task Response db
			# "time_stamp":{"user_id":"marzipan","task_id":"8",
			# "response_type":"preferred_verticals",
			# "response_value":"Images , Wiki , General Web"}
			new_entry = [entry , values['user_id'] , int(values['task_id']),\
                values['response_type'], \
                values['response_value']]
			tsv_data.append(new_entry)

    # create a new data frame 
    tsv_frame = pd.DataFrame(tsv_data, columns= dbcolumns)
    # sort by time key
    tsv_frame = tsv_frame.sort(sort_keys)

    return tsv_frame 

def FormatQueryResultDB(databases, dbcolumns, sort_keys ):
    tsv_data = []
    for database in databases:
        for entry , values in database.items():
            # Format of Query Result db
            # "1462466899610":{"user_id":"Manisha","query_id":4,"task_id":"4","query_text":"pythagoras theorem","page_id":1,"search_results":[["i",[{"title":"Pythagorean Theorem Worksheets | Practicing Pythagorean Theorem ...","external_url":"http://www.math-aids.com/images/pythagorean-definition-01.png","display_url":"www.math-aids.com/Pythagorean_Theorem","thumbnail":"http://ts2.mm.bing.net/th?id=OIP.M76e12a7ce2b8773ab540eb6eebcb1671H0&pid=15.1"},{"title":"Cribbd - What shape do you use the Pythagoras theorem?","external_url":"http://www.k6-geometric-shapes.com/image-files/pythagoras-theorem.jpg","display_url":"cribbd.com/question/what-shape-do-you-use-the-pythagoras-theorem","thumbnail":"http://ts2.mm.bing.net/th?id=OIP.M1903351061b3334a50ae403a4ed6bdabH0&pid=15.1"},{"title":"Pythagorean Theorem","external_url":"http://www.crewtonramoneshouseofmath.com/images/pythagorean-theorem.gif","display_url":"www.crewtonramoneshouseofmath.com/pythagorean-theorem.html","thumbnail":"http://ts3.mm.bing.net/th?id=OIP.M8857398b2e0e5db80fa99a7720100499H0&pid=15.1"},{"title":"Pythagorean Theorem Worksheets | Practicing Pythagorean Theorem ...","external_url":"http://www.math-aids.com/images/pythagorean-definition-04.png","display_url":"www.math-aids.com/Pythagorean_Theorem","thumbnail":"http://ts3.mm.bing.net/th?id=OIP.M43f0a5648998ba44aa9f58947f814640H0&pid=15.1"},{"title":"Pythagoras' (Pythagorean) Theorem","external_url":"http://www.storyofmathematics.com/images2/pythagoras_theorem.gif","display_url":"www.storyofmathematics.com/greek_pythagoras.html","thumbnail":"http://ts2.mm.bing.net/th?id=OIP.Mb59b15c738ea277714c166a67f8ed0e4H0&pid=15.1"},{"title":"Pythagoras Theorem Formula","external_url":"http://ncalculators.com/images/pythagoras-theorem.gif","display_url":"ncalculators.com/number-conversion/pythagoras-theorem.htm","thumbnail":"http://ts1.mm.bing.net/th?id=OIP.M8a9e3735630bffd9428e26cf505fda25H0&pid=15.1"},{"title":"The Pythagoras Theorem","external_url":"http://www.petervis.com/mathematics/Pythagoras_Theorem/Pythagoras_Theorem/Pythagoras_Theorem_Formula.gif","display_url":"www.petervis.com/mathematics/Pythagoras_Theorem/Pythagoras_Theorem...","thumbnail":"http://ts2.mm.bing.net/th?id=OIP.M9747de5fc2281f6e2daa3499810d2840H0&pid=15.1"}]],["o",{"title":"Pythagorean theorem - Wikipedia, the free encyclopedia","desc":"In mathematics, the Pythagorean theorem, also known as Pythagoras' theorem, is a fundamental relation in Euclidean geometry among the three sides of a right triangle.","display_url":"https://en.wikipedia.org/wiki/Pythagorean_theorem","external_url":"https://en.wikipedia.org/wiki/Pythagorean_theorem"}],["o",{"title":"The Pythagorean Theorem - University of Georgia","desc":"The Pythagorean Theorem was one of the earliest theorems known to ancient civilizations. This famous theorem is named for the Greek mathematician and philosopher ...","display_url":"jwilson.coe.uga.edu/.../EMT.669/Essay.1/Pythagorean.html","external_url":"http://jwilson.coe.uga.edu/emt669/Student.Folders/Morris.Stephanie/EMT.669/Essay.1/Pythagorean.html"}],["o",{"title":"Pythagoras Theorem - Maths Resources","desc":"It is called \"Pythagoras' Theorem\" and can be written in one short equation: a 2 + b 2 = c 2. Note: c is the longest side of the triangle; a and b are the other two sides","display_url":"www.mathsisfun.com/pythagoras.html","external_url":"http://www.mathsisfun.com/pythagoras.html"}],["o",{"title":"Pythagoras - Wikipedia, the free encyclopedia","desc":"Pythagorean theorem. A visual proof of the Pythagorean theorem. Since the fourth century AD, Pythagoras has commonly been given credit for discovering the ...","display_url":"https://en.wikipedia.org/wiki/Pythagoras","external_url":"https://en.wikipedia.org/wiki/Pythagoras"}],["o",{"title":"Pythagorean Theorem -- from Wolfram MathWorld","desc":"Many different proofs exist for this most fundamental of all geometric theorems. The theorem can also be generalized from a plane triangle to a trirectangular ...","display_url":"mathworld.wolfram.com/PythagoreanTheorem.html","external_url":"http://mathworld.wolfram.com/PythagoreanTheorem.html"}],["o",{"title":"Intro to the Pythagorean theorem 1 | The Pythagorean ...","desc":"Sal introduces the famous and super important Pythagorean theorem!","display_url":"https://www.khanacademy.org/.../v/the-pythagorean-theorem","external_url":"https://www.khanacademy.org/math/basic-geo/basic-geo-pythagorean-topic/basic-geo-pythagorean-theorem/v/the-pythagorean-theorem"}],["o",{"title":"Pythagorean Theorem - Mathwarehouse.com","desc":"How to use the pythagorean theorem, explained with examples,practice problems, a vidoe tutorial and pictures.","display_url":"www.mathwarehouse.com/.../how-to-use-the-pythagorean-theorem.php","external_url":"http://www.mathwarehouse.com/geometry/triangles/how-to-use-the-pythagorean-theorem.php"}],["o",{"title":"Pythagorean Theorem and its many proofs - Cut-the-Knot","desc":"116 proofs of the Pythagorean theorem: squares on the legs of a right triangle add up to the square on the hypotenuse","display_url":"www.cut-the-knot.org/pythagoras/index.shtml","external_url":"http://www.cut-the-knot.org/pythagoras/index.shtml"}],["o",{"title":"Proofs of the Pythagorean Theorem","desc":"Bhaskara's Second Proof of the Pythagorean Theorem In this proof, Bhaskara began with a right triangle and then he drew an altitude on the hypotenuse.","display_url":"jwilson.coe.uga.edu/.../HeadAngela/essay1/Pythagorean.html","external_url":"http://jwilson.coe.uga.edu/EMT668/EMT668.Student.Folders/HeadAngela/essay1/Pythagorean.html"}]]}

            search_results = values['search_results']

            # The documents are stored in oreder in which
            # they are displayed on the search results
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
                doc_url = doc_prop['display_url']
               
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

    return tsv_frame 




def main():
    parser = argparse.ArgumentParser(description='Find and plot statistics\
            about vertical search related data.')
    parser.add_argument('-p','--pageResponseDB', help='Page response db from the\
            interface',required=True)
    parser.add_argument('-t','--taskResponseDB', help='Task response db from the\
            interface',required=True)
    parser.add_argument('-q','--queryResultDB', help='Query result db from the\
            interface',required=True)
    parser.add_argument('-f','--isFolder', help='Indicate whether database\
    is in one file or files in one folder',action='store_true')

    arg = parser.parse_args()
    page_response_db = []
    task_response_db = []
    query_result_db = []

    # If a single event and response db file
    if not arg.isFolder:
        p_db = ReadDB(open(arg.pageResponseDB,'r'))
        page_response_db.append(p_db)

        t_db = ReadDB(open(arg.taskResponseDB,'r'))
        task_response_db.append(t_db)

        q_db = ReadDB(open(arg.queryResultDB,'r'))
        query_result_db.append(q_db)
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

            
	# Format page response db
    page_response_table = FormatPageResponseDB(page_response_db, page_response_header, page_reponse_sortkeys)

    # Format task response db
    task_response_table = FormatTaskResponseDB(task_response_db,task_response_header,task_response_sortkeys)

    # Format query result db
    query_result_table = FormatQueryResultDB(query_result_db,query_result_header,query_result_sortkeys)

    # Remove test users
    page_response_table = page_response_table[~page_response_table['user_id'].str.contains('test')]
    task_response_table = task_response_table[~task_response_table['user_id'].str.contains('test')]
    query_result_table = query_result_table[~query_result_table['user_id'].str.contains('test')]

    # a. task : users. Compute the number of users who provided task feedback
    #task_response_table[['task_id','user_id']].to_csv('task.csv')
    task_response_table.groupby(['task_id']).agg({'user_id':pd.Series.nunique}).to_csv('task_feedback.csv')

    # b. task : user_impressions. Compute the number of users who executed a task.
    #page_response_table[['task_id','user_id']].to_csv('page.csv')
    page_response_table.groupby(['task_id']).agg({'user_id':pd.Series.nunique}).to_csv('task_execute.csv')

    # c. task : vertical_views. Compute the number of times each vertical was shown as top result. 
    #query_result_table[['task_id','user_id']].to_csv('query.csv')
    query_results = query_result_table[query_result_table['page_id']==1]
    query_results.groupby(['task_id','doc_type','doc_pos']).count().to_csv('vertical_pos.csv')

    # d. task : queries. Compute the number of queries fired for the task.
    query_result_table.groupby(['task_id']).agg({'query_text':pd.Series.nunique}).to_csv('task_queries.csv')

if __name__ == "__main__":
    main()
