// TODO(mverma): Query autocompletion. 
// TODO(mverma): Parse search results json

var request = require('sync-request');
var changeCase = require("change-case");
var array_utils = require("underscore");
var base64 = require('base-64');
var math = require('mathjs');
var ReadWriteLock = require('rwlock');

// For updating the result type shown to a user.
var lock = new ReadWriteLock();

// Stores task preferences
var task_preferences = {};

// Queue that manages first result. 
var first_result_queues = {};

var account_key = 'hTAHc8JGEP57nkCFiKPUlmevu5aaQIZfYniGYV3hH/0';
var bing_uri = 'https://api.datamarket.azure.com';
var wiki_uri = 'http://en.wikipedia.org';


function GetSearchResults(query_text, page_number, type, result_count, removeWiki)
{
	param = null;
	authorization = '';
	if (!(type == 'Wiki'))
	{
	  params = '/Bing/Search/'+type+'?$format=json&$top='+result_count+ 
			  '&$Skip='+10*(page_number-1)+'&Market=\'en-US\'&Query=' + query_text ;
	  console.log(params);
	  authorization ='Basic ' + base64.encode(account_key+ ':' + account_key);
	  search_uri = bing_uri;
	}
	else {
		search_uri = wiki_uri;
		params = '/w/api.php?format=json&action=query&generator=search&gsrnamespace=0&gsrlimit=1&prop=pageimages|extracts&pilimit=max&exintro&explaintext&exsentences=1&exlimit=max&pithumbsize=200&gsrsearch='+query_text;
	}

	var response = request('GET',search_uri+params, 
			  { 'headers' : {
					'User-Agent': 'request',
					'Authorization' : authorization,
					'Content-Type': 'application/x-www-form-urlencoded'
			  }});
	results = JSON.parse(response.getBody('utf8'));

	var search_results = [];
	if (!(type == 'Wiki'))
	{
		// Create result array.
		// Video : (["v", {"title" : "Title","time" : "RunTime" , "external_url" : "MediaUrl",
		//		"display_url" : "DisplayUrl", "thumbnail" : "Thumbnail"} ]);
		// Image : (["i", {"title" : "Title" , "external_url" : "MediaUrl",
		//		"display_url" : "DisplayUrl", "thumbnail" : "Thumbnail"} ]);
		// Web : (['o', {"title": "Title", "desc":"description", "display_url": "DisplayUrl", 
		//		"external_url":"Url"}]);
		if (results.d !== undefined)
		{ 
			var items = results.d.results;
			console.log(items.length);

			for (var k = 0, len = items.length; k < len; k++)
			{
				var item = items[k];
				switch (item.__metadata.type)
				{
					case 'WebResult':
						// If wiki result and it has to be ignored, i.e.
						// removeWiki = true
						if (removeWiki && item.DisplayUrl.indexOf("wikipedia") != -1)
						  continue;
						search_results.push([ "o" , {"title" :item.Title , 
							"desc": item.Description,
							"display_url": item.DisplayUrl , 
							"external_url": item.Url } ] );
						break;
					case 'ImageResult':{
						if (search_results.length == 0)
							search_results.push(["i", []] );
			  
						search_results[0][1].push({"title" : item.Title ,
							"external_url" : item.MediaUrl,	
							"display_url" : item.DisplayUrl, 
							"thumbnail" : item.Thumbnail.MediaUrl});
						break;
					  }
					case 'VideoResult':{
						var runTime = (item.RunTime != null) ? parseInt(item.RunTime) : 0;
						var totalSecs = runTime / 1000;
						var hours = math.round(totalSecs / 3600,0);
						var mins = math.round(hours / 60,0);
						var secs = totalSecs % 60; 
						var time_string = '';
						if (secs > 0)
							time_string = secs+' secs';
						if (mins > 0)
							time_string = mins+' mins '+time_string;
						if (hours > 0)
							time_string = hours +' hours '+time_string;
						search_results.push(["v", {"title" : item.Title,
						   "time" : time_string , 
						   "external_url" : item.MediaUrl,
						   "display_url" : item.DisplayUrl, 
						   "thumbnail" : item.Thumbnail.MediaUrl}] );
						break;
					}
				}
			}
		}
	}
	else
	{
		// Create a result array
		// Wiki : ([''w, {"title": "title", "desc":"extract", "display_url": "external_url (next)", 
		//		"external_url":https://en.m.wikipedia.org/wiki?curid=+"Url", "thumbnail": "thumbnail"}]);
		console.log('In wiki');

		if(results.query !== undefined)
		{
			var items = results.query.pages;
			for (var k in items)
			{
				var item = items[k];
				var source = '';
				if (item.thumbnail !== undefined)
					source =  item.thumbnail.source;
				var page_url = "https://en.m.wikipedia.org/wiki?curid="+item.pageid;
				search_results.push(['w', {"title": item.title, "desc":item.extract, "display_url":page_url , 
				"external_url": page_url, "thumbnail":source }]);
			}
		}
	}
	return search_results;
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
		var first_result_type = null;

		if (page_number == 1)
		{
			// Acquire a lock to change the queue
			// If two people query synonymously change queue safely.
			lock.readLock(function (release) {
			  first_result_type = first_result_queues[task_id].shift();
			  console.log('Fetching results for '+query_text+' for '+first_result_type);
			  lock.writeLock(function (release) {
	  			  // Shift the queue.
				  first_result_queues[task_id].push(first_result_type);
				  release();
			  });
			  release();
			});

			// Fix the number of elements in image.
			var num_elements = 1;
			if (first_result_type == 'Image')
				num_elements = 7;
			if (first_result_type == 'Web')
				num_elements = 10;
	
			var removeWiki = false;

			// Fetch the first result.
			if (first_result_type == 'Wiki') {
				search_results = search_results.concat(
						GetSearchResults(query_text, page_number, 
						first_result_type,num_elements, removeWiki));
				removeWiki = true;
			}
			else				
				search_results = search_results.concat(
						GetSearchResults(query_text, page_number, 
						first_result_type, num_elements,removeWiki));

			//// Fetch the remaining results from Web.
			num_elements = 10 - search_results.length;
			if (num_elements > 0)
			  search_results = search_results.concat(GetSearchResults(query_text, 
						page_number, 'Web', num_elements,removeWiki));
	   }
	   else
	   {
			// Return the remaining 10 results after page_number 
		  	// they are web only results.
		  	search_results = search_results.concat(GetSearchResults(query_text, 
						page_number, 'Web', 10));
	   }
	  return search_results;
	}
};
