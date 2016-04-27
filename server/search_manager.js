// TODO(mverma): Query autocompletion. 
// TODO(mverma): Parse search results json

var request = require('sync-request');
var changeCase = require("change-case");
var array_utils = require("underscore");
var base64 = require('base-64');


var SearchSource = Object.freeze({BING: 0, WIKIPEDIA: 1})

// Stores task preferences
var task_preferences = {};

// Queue that manages first result. 
var first_result_queues = {};

var account_key = 'hTAHc8JGEP57nkCFiKPUlmevu5aaQIZfYniGYV3hH/0';
var bing_uri = 'https://api.datamarket.azure.com';
var wiki_uri = 'http://en.wikipedia.org';

function GetSearchResults(query_text, page_number, type, result_count)
{
	param = null;
	authorization = '';
	if (!(type == 'Wiki'))
	{
	  params = '/Bing/Search/'+type+'?$format=json&$top='+result_count+ 
			  '&$Skip='+10*(page_number-1)+'&Market=\'en-US\'&Query=' + query_text ;
	  authorization ='Basic ' + base64.encode(account_key+ ':' + account_key);
	  search_uri = bing_uri;
	}
	else {
		search_uri = wiki_uri;
		params = '/w/api.php?format=json&action=query&generator=search&gsrnamespace=0&gsrlimit=1&prop=pageimages|extracts&pilimit=max&exintro&explaintext&exsentences=2&exlimit=max&&pithumbsize=100&gsrsearch='+query_text;
	}

	var response = request('GET',search_uri+params, 
			  { 'headers' : {
					'User-Agent': 'request',
					'Authorization' : authorization,
					'Content-Type': 'application/x-www-form-urlencoded'
			  }});
	results = JSON.parse(response.getBody('utf8'));

	if (!(type == 'Wiki'))
	{
		// Create result array.
		//
		// Video : search_results.push(["v", {"title" : "","time" : "" , "external_url" : "",
		//		"display_url" : "", "thumbnail" : ""} ]);
		// Image : search_results.push(["i", {"" : "","time" : "" , "external_url" : "",
		//		"display_url" : "", "thumbnail" : ""} ]);


		return results['d']['results'];

	}
	else
	{
		// Create a result array
		return results['query']['pages'];
	
	
	}
}

// Generate the results for a single query.
module.exports = {

	setTaskPreferences: function (task_desc_dict, pref_string ){
		for (var task_id in task_desc_dict)
		{
		  // this task has not been assigned before. 
		  task_preferences[task_id] = task_desc_dict[task_id][pref_string];
		  // console.log('Original pref '+task_id+' '+ task_preferences[task_id]);
		  // Take the preferences and randomly permute the list.
		  first_result_queues[task_id] = array_utils.shuffle(task_preferences[task_id]);
		  // console.log('Randomized pref '+task_id+' '+first_result_queues[task_id]);
		  
		}
	},

	searchQuery: function(user_name, task_id, query_text, page_number) {
		// Fix the query text.
		var search_results = [];
		query_text ="'"+ changeCase.lowerCase(query_text)+"'";
		query_text = encodeURI(query_text);
		console.log(query_text+' '+task_id+' '+user_name+' '+page_number);

		if (page_number == 1)
		{
			var first_result_type = first_result_queues[task_id].shift();

			console.log('Fetching results for '+query_text+' for '+first_result_type);
			// Shift the queue.
			first_result_queues[task_id].push(first_result_type);

			// Send dummy video results 
			// Video : (Title, time, external_url, display_url, thumbnail_image_source)
			// Image :
			// Wiki :
			// Web : 
			/*
			// Fix the number of elements in image.
			var num_elements = 1;
			if (first_result_type == 'Image')
				num_elements = 9;
		
			// Fetch the first result.
			if (first_result_type == 'Wiki')
				search_results.push(GetWikiResults(query_text));
			else				
				search_results.push(GetBingResults(query_text, page_number, 
					first_result_type, num_elements));

			//// Fetch the remaining results from Web.
			num_elements = 10 - search_results.length;
			search_results = search_results.concat(GetBingResults(query_text, page_number, 
						'Web', num_elements));
			*/
	   }
	   else
	   {
			// Return the remaining 10 results after page_number 
		  	// they are web only results.
		  	search_results = search_results.concat(GetBingResults(query_text, page_number, 
						'Web', 10));
	   }
	  return search_results;
	}
};
