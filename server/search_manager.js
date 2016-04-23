// 1. Fetch the results from Microsoft API
// 2. Display the results from Fedweb. 
// ----------------------------------------

var VerticalEnum = Object.freeze({IMAGE: 0, VIDEO: 1, WIKI: 2, OTHER:3});

// Queue that manages first result. 
first_result_queues = {}


// Generate the results for a single query.
module.exports = {

	searchQuery: function(user_name, task_id, pref_order, query_text) {
		if (!(task_id in first_result_queues))
		{
		  // this task has not been assigned before. 
		  // Take the preferences and randomly permute the list.


		}


	}



};



// Set up the 

