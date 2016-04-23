//TODO (mverma) : How to update the task list once 
//				user submits feedback for current task.

var fs = require('fs');
var MicroDB = require('nodejs-microdb');

// Define all the databases.

// global counts of queries and clicked documents.
var global_query_id = 0;
var global_clicked_doc_id = 0;

// User query database
var query_database = new MicroDB({'file':'query.db', 'defaultClean':true});

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
	loadTaskIdAndVerticals: function(task_file){
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
     	           // format : task_id, task_description, task_pref in 3
				   // verticals
     	           if(split.length == 3)
     	           	task_des_dict[split[0]].push({'desc':split[1],'pref_order': [split[2], split[3], split[4]]});
     	           else
     	               console.log('Error in task file in line '+i+' '+split.length);
     	        }
     	        return task_desc_dict;
     	}
     	catch(error)
     	{
     	        console.log('Attempt to load incorrect file '+filepath );
     	        return false;
     	}
	},
	
	// Add user query
	addUserQuery: function(user_name,task_id, query_text, timestamp){
  
	  // Update the query database.
	  query_database.add({'user_id':user_name , 'query_id':global_query_id,
		  'task_id':task_id, 'query_text':query_text}, timestamp);

	  var query_id = global_query_id;

	  // Increment global_query_id
	  global_query_id++;
	
	  return [query_id,;
	}, 
	
	// Add clicked document
	addClickDoc: function(user_name,task_id, query_id, doc_id, doc_url, timestamp){
	  // Update the click database.
	  click_database.add({'user_id':user_name , 'query_id':query_id,
		  'task_id':task_id, 'doc_id':doc_id, 'doc_url':doc_url}, timestamp);

	  // Increment global_query_id
	  global_clicked_doc_id++;
	
	  return true;
	},

	// Add serp event
	addSerpEvent: function(user_name, task_id, query_id, doc_id, event_type, event_value, event_dist, timestamp){ 

	  click_database.add({'user_id':user_name , 'query_id':query_id,
		  'task_id':task_id, 'doc_id':doc_id, 'event_type':event_type,
		  'event_value':event_value,'event_dist':event_dist}, timestamp);

	},

	// Add task response
	addTaskResponse: function(user_name, task_id, response_type, response_value, timestamp){

	  task_response_database.add({'user_id':user_name , 'task_id':task_id,
		  'response_type':response_type, 'response_value':response_value}, timestamp);

	  // finished the task. Update the user task complete dictionary.
	  user_task_complete_dict[user_name].push(task_id);

	},

	// Update the page response database.
	addPageResponse: function(user_id, task_id, query_id, doc_id, response_type, response_value, timestamp){

	  page_response_database.add({'user_id':user_name , 'query_id':query_id,
		  'task_id':task_id, 'doc_id':doc_id, 'response_type':response_type,
		  'response_value':response_value}, timestamp);
	}
};



