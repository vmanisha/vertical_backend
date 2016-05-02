//TODO (mverma) : How to update the task list once 
//				user submits feedback for current task.
// TODO (mverma) : Add lock to global document click count. 
var fs = require('fs');
var MicroDB = require('nodejs-microdb');

// Define all the databases.

// global counts of queries and clicked documents.
var global_clicked_doc_id = 0;
var last_query_search_results = {};
var last_query_doc_click = {};

// User query database
var query_results_database = new MicroDB({'file':'query_result.db', 'defaultClean':true});

// User clicked document database
var click_database = new MicroDB({'file':'click.db', 'defaultClean':true});

// SERP event database
var event_database = new MicroDB({'file':'serp_event.db', 'defaultClean':true});

// Response DB
var task_response_database  = new MicroDB({'file':'task_response.db', 'defaultClean':true});

// Page Response DB
var page_response_database  = new MicroDB({'file':'page_response.db', 'defaultClean':true});


module.exports = {
	// Load the task dictionary with vertical preferences. 
	// Tab seperated file containing task_id, description
	// and preferred vertical. 
	loadTaskIdDescPref: function(task_file){
		var task_desc_dict = {};
     	var filepath = __dirname+'/'+task_file;
     	try
     	{
     	        var array = fs.readFileSync(filepath).toString().split("\n");
     	        console.log('Loading Tasks from '+filepath+' of length '+array.length);
     	        //load the task_id, description and prefered vertical. 
     	        for (var i in array)
     	        {
     	        	var split = array[i].split('\t');
     	           // format : task_id, task_query, task_description, task_pref in 4
				   // verticals (img, video, wiki, organic)
     	           if(split.length == 7)
					   task_desc_dict[split[0]] = {'task_query':split[1], 'task_desc':split[2],
						'task_pref_order': [split[3].trim(), split[4].trim(), split[5].trim(), split[6].trim()]};
     	           else
     	               console.log('Error in task file in line '+i+' '+split.length);
     	        }
     	        return task_desc_dict;
     	}
     	catch(error)
     	{
     	        console.log('Error loading file '+filepath+ ' '+error );
     	        return false;
     	}
	},

	// In case user was working on the task and was interupted. Send the last state
	// of the task <query_id, page_id, query_text and results>.
	getLastUserAndTaskState: function (user_name, task_id) {
	  
		if( (user_name in last_query_search_results) && (task_id in last_query_search_results[user_name]))
		{
		  console.log("User searched for this task before. Username "+user_name+" and task "+task_id+" "+
						last_query_search_results[user_name][task_id].length);
		  var search_result_array = last_query_search_results[user_name][task_id];
		  if (search_result_array.length > 0)
		  {
			  var array =search_result_array[search_result_array.length -1];
			  return { 'query_id' : array['query_id'],"page_id" : array["page_id"], 
						"query_text" : array["query_text"],
						'search_results' : array['search_results'] };
		  }
		}
		return null;
	}, 

	getLastUserTaskQueryClick: function (user_name, task_id) {
		
		if( (user_name in last_query_doc_click) && (task_id in last_query_doc_click[user_name]))
		{
		  console.log("User clicked some doc before. Username "+user_name+" and task "+task_id+" "+
						last_query_doc_click[user_name][task_id].length);
		  var doc_click_array = last_query_doc_click[user_name][task_id];
		  return doc_click_array[doc_click_array.length -1];
		}
		return null;
	}, 

	// Check if user query was fired previously in the task session.
	checkQueryAndPageInHistory: function(user_name,task_id, user_query, page_id){
 
	  // If the user_name and task_id exist return the query
	  // and page_id.
	  if( (user_name in last_query_search_results) && (task_id in last_query_search_results[user_name]))
	  {
		  console.log("Found user and task searches "+last_query_search_results[user_name][task_id].length);
		  var search_result_array = last_query_search_results[user_name][task_id];
		  for (var i = (search_result_array.length-1); i > -1 ; i--)
		  {
			  var stored_query = search_result_array[i]['query_text'];
			  var stored_page = search_result_array[i]['page_id'];

			  if(stored_query == user_query && stored_page == page_id)
			  return { 'query_id' : search_result_array[i]['query_id'],
				  'search_results' : search_result_array[i]['search_results'] };
		  }
	  }

	  // this is a new query.
	  return null;

	},

	// By now we know that the query and page id do not exist for a user and
	// task.
	addSearchResults: function(user_name, task_id, query_id, query_text, 
								   page_id, search_results, timestamp) {
	  // Update the query database.
	  query_results_database.add({'user_id':user_name , 'query_id':query_id,
		  'task_id':task_id, 'query_text':query_text, 'page_id' : page_id, 
		  'search_results': search_results } , timestamp);

	  // Update the last query stats for this user and task.
	  if(user_name in last_query_search_results)
	  {
		  if (task_id in last_query_search_results[user_name])
			last_query_search_results[user_name][task_id].push({ 'query_id' : query_id,
			  'page_id': page_id, 'query_text': query_text, 'search_results': search_results });

		  		 
		  // A user may choose not to submit task feedback :(
		  // So, there may be multiple tasks. 
		  else
		  last_query_search_results[user_name][task_id] = [{ 'query_id' : query_id,
			  'page_id': page_id, 'query_text': query_text, 'search_results': search_results }];
	  }
	  else{
		  // First visit of the user.
		 last_query_search_results[user_name] =  {};
		 last_query_search_results[user_name][task_id] = [{ 'query_id' : query_id,
			  'page_id': page_id, 'query_text': query_text, 'search_results': search_results }];
	  }
	  
          console.log("Adding results for "+ user_name+" "+task_id + 
			" "+query_text + " "+ query_id + " "+page_id +" " + 
			last_query_search_results[user_name][task_id].length);
	  return true;
    },
	
	
	// Add clicked document
	addClickDoc: function(user_name,task_id, query_id, page_id, doc_id, doc_url, timestamp){
	  // Update the click database.
	  click_database.add({'user_id':user_name , 'query_id':query_id, "page_id" : page_id, 
		  'task_id':task_id, 'doc_id':doc_id, 'doc_url':doc_url}, timestamp);

	  // Store the last click. 
	  // Update the last query click stats for this user and task.
	  if(user_name in last_query_doc_click)
	  {
		  if (task_id in last_query_doc_click[user_name])
			last_query_doc_click[user_name][task_id].push({'query_id' : query_id,
			  'page_id': page_id, 'doc_id': doc_id, 'doc_url': doc_url });
		  // A user may choose not to submit task feedback :(
		  // So, there may be multiple tasks. 
		  else
		  last_query_doc_click[user_name][task_id] = [{ 'query_id' : query_id,
			  'page_id': page_id, 'doc_id': doc_id, 'doc_url': doc_url }];
	  }
	  else{
		  // First click of the user.
		 last_query_doc_click[user_name] =  {};
		 last_query_doc_click[user_name][task_id] = [{ 'query_id' : query_id,
			  'page_id': page_id, 'doc_id': doc_id, 'doc_url': doc_url  }];
	  }


	  global_clicked_doc_id++;
	  return true;
	},

	// Add serp event
	addSerpEvent: function(user_name, task_id, query_id, doc_id, event_type, 
						  event_value, event_dist, timestamp){ 

	  click_database.add({'user_id':user_name , 'query_id':query_id,
		  'task_id':task_id, 'doc_id':doc_id, 'event_type':event_type,
		  'event_value':event_value,'event_dist':event_dist}, timestamp);

	  return true;
	},

	// Add task response
	addTaskResponse: function(user_name, task_id, response_type, response_value, 
							 timestamp){

	  task_response_database.add({'user_id':user_name , 'task_id':task_id,
		  'response_type':response_type, 'response_value':response_value}, timestamp);

	  // finished the task. Update the user task complete dictionary.
	  user_task_complete_dict[user_name].push(task_id);
	  
	  // Write to the databases and clear the cache.
	  task_response_database.flush();
	  page_response_database.flush();
	  click_database.flush();
	  query_results_database.flush();
	  event_database.flush();

	  // Given that task is finished, remove the session from session array.
	  delete last_query_search_results[user_name][task_id];
	  delete last_query_doc_click[user_name][task_id];

	  return true;
	},

	// Update the page response database.
	addPageResponse: function(user_id, task_id, query_id, page_id, doc_id, response_type, 
							 response_value, timestamp){
	  
	  page_response_database.add({'user_id':user_name , 
		  'task_id':task_id, 'query_id' : query_id, 'page_id' : page_id, 
		  'doc_url':doc_id, 'response_type':response_type,
		  'response_value':response_value}, timestamp);
	  return true;
	}
};



