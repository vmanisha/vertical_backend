// TODO (mverma): Set the parameters for first visit.
var express = require('express');
var app = express();
var engines = require('consolidate');
var math = require('mathjs');
var bodyParser = require('body-parser');
var database = require('./database');
var search_manager = require('./search_manager');
var ReadWriteLock = require('rwlock');

var request = require('request');
var fs = require('fs');
var url = require('url');
var cheerio = require('cheerio');

// For updating the result type shown to a user.
var lock = new ReadWriteLock();

// Global query_id 
var global_query_id = 0;

// Global page index
// Contains url to page location mapping
var global_page_location_dict = {}
var saved_pages_count = 0;

// Task list dictionary
// task_id : [task_pref, task_desc]
var task_file = 'task_descriptions.txt';
var task_desc_dict = database.loadTaskIdDescPref(task_file);

// task_pref_order is the key to access preferences from
// task_desc_dict
search_manager.setTaskPreferences(task_desc_dict, 'task_pref_order');

// Use body parser
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.set('views', __dirname + '/../views');
app.use("/", express.static(__dirname + '/../views'));
app.use("/js", express.static(__dirname + '/../views/js'));
app.use("/css", express.static(__dirname + '/../views/css'));
app.use("/img", express.static(__dirname + '/../views/img'));

// set the view engine to ejs
app.set('view engine', 'ejs');

app.get('/', function(req, res) {
  // res.type('text/html'); // set content-type
  var task_id = math.round(math.random(1,10));
  res.render('index.ejs', {
	  "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify("Guest"), "search_page_id": JSON.stringify(1),
	  "user_query" : JSON.stringify(task_desc_dict[task_id]['task_query']), 
	  "query_id" : JSON.stringify(1), "results" : JSON.stringify({}), 
	  "task_description" : JSON.stringify(task_desc_dict[task_id]['task_desc'])
  });
});


// The user is just beginning a task. No search query or
// page id is recieved. 
app.get('/begin', function(req, res) {
  var task_id = req.query.task;
  var user_name = req.query.user;
  var query_text =req.query.query;

  // check what was the last entry of user for the task.
  // If it is present send it.
  var last_history_state = database.getLastUserAndTaskState( user_name, task_id);

  if (last_history_state == null)
    res.render('index.ejs', {
	  "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify(user_name), "search_page_id": JSON.stringify(1),
	  "user_query" : JSON.stringify(query_text), "query_id" : JSON.stringify(""),
	  "results" : JSON.stringify({})});
  else {
  // else send a new search page with input query. 
	  res.render("index.ejs", { "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify(user_name), 
	  "search_page_id": JSON.stringify(last_history_state["page_id"]),
	  "user_query" : JSON.stringify(last_history_state["query_text"]), 
	  "query_id" : JSON.stringify(last_history_state["query_id"]),
	  'results': JSON.stringify(last_history_state["search_results"])});

	  // Submit an event for search. 
  }
  
});

//----------------------------------------------
// USER MANAGEMENT
//----------------------------------------------
// Register a user with user name and id. 
app.get('/registerUser', function(req, res){

	var task_dict = {};
	var user_name = req.query.user;
	// Return the list of tasks not finished. 
	for (var task_id in task_desc_dict)
		task_dict[task_id] = [task_desc_dict[task_id]['task_query'],
								  task_desc_dict[task_id]['task_desc']] ;
	res.json(task_dict);
});

//----------------------------------------------
// SEARCH REQUEST MANAGEMENT
//----------------------------------------------

// Search a query using ms api and present the results. 
app.get('/search', function(req, res){
  var task_id = req.query.task;
  var query_text =req.query.query;
  var user_name = req.query.user;
  var page_number = parseInt(req.query.page);
  var time = parseInt(req.query.time);

  // Check if this is a repeated request. If yes
  // get the results and send them again.
  var check_result = database.checkQueryAndPageInHistory(user_name, task_id, 
	  query_text, page_number);

  var query_id = null;

  // If the result is undefined 
  if (check_result == null)
  {
	  // Acquire a lock to assign query id
	  lock.readLock(function (release) {
		query_id = global_query_id;
		lock.writeLock(function (release) {
		  global_query_id++;
		  release();
		});
		release();
	  });

	  console.log('New request for query_id: '+query_id+', query: '+query_text+
			' task_id: '+task_id +' user_id: '+user_name+' page_id: '+page_number);
	  // given the task and user query, prepare the search result
  	  // page and render that. Keep the global_query_id in page.
  	  var results = search_manager.searchQuery(user_name, task_id, 
	   query_text, page_number);
	  
	  // Save the search results for future use. 
	  database.addSearchResults(user_name, task_id, query_id, query_text, 
			  page_number, results, time);

	  res.render("index.ejs", { "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify(user_name), 
	  "search_page_id": JSON.stringify(page_number),
	  "user_query" : JSON.stringify(query_text), 
	  "query_id" : JSON.stringify(query_id),
	  'results': JSON.stringify(results)});
  }
  else {
	  res.render("index.ejs", { "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify(user_name), 
	  "search_page_id": JSON.stringify(page_number),
	  "user_query" : JSON.stringify(query_text), 
	  "query_id" : JSON.stringify(check_result['query_id']),
	  'results':JSON.stringify(check_result['search_results'])});

	  // Add a search event. 
  }


});


// Submit serp interaction to db.
app.post('/submitPageEvent', function(req, res){

  database.addPageEvent(req.body.url, req.body.eventtype,
  req.body.eventvalue, req.body.eventtime);
  res.json(true);
});

// Submit page interaction to db.
app.post('/submitPageClick', function(req, res){
  console.log("Click : user: "+req.body.user+" task_id: "+req.body.task+" url: "
	+req.body.docurl+" doc_id: "+req.body.docid+" query_id: "+req.body.queryid+
	' page_id: ' + req.body.page + ' time' + req.body.time);

  if (req.body.user && req.body.docurl && req.body.task && 
	  req.body.queryid && req.body.page && req.body.docid) {

		  database.addClickDoc(req.body.user, req.body.task,
		  req.body.queryid, req.body.page, req.body.docid, 
		  req.body.docurl, req.body.time);
  }
  	  res.json(true);
});

// Submit page responses (relevance and satisfaction) interaction to db.
app.post('/submitPageResponse', function(req, res){
  var response_array = req.body.responses;

  var time = req.body.time;
  // Ideally the click is registered in a global database. 
  // So fetch last click information. 
  console.log("Page Response : user: "+req.body.user+" task_id: "+
		  req.body.task+ " doc_url: "+req.body.docurl);
  if (response_array !== undefined)
  {
	  for(var i = 0; i < response_array.length;i++) 
	  {
		for(var rkey in response_array[i])
		{
		   time = new Date(time.getTime()+10+i);
		   database.addPageResponse(req.body.user, req.body.task, 
		   req.body.docurl, rkey,response_array[i][rkey],time);
		}
	  }
  }
  res.json({"success":true});

});

// Submit task responses (relevance and satisfaction) interaction to db.
app.post('/submitTaskResponse', function(req, res){
  var response_array = req.body.responses;
  var time = req.body.time;
  console.log("Task Response : user: "+req.body.user+" task_id: "+
		  req.body.task+ "response_array: "+response_array);
  for(var i = 0; i < response_array.length;i++) 
  {
	for(var rkey in response_array[i])
	  {
		  database.addTaskResponse(req.body.user, req.body.task,
		  rkey,response_array[i][rkey],time);
	  }
    }
  res.json({"success":true});
});

//-------------------------------------------------------


//-------------------------------------------------------
// PAGE MANAGEMENT
//-------------------------------------------------------

app.get('/viewPage', function (req, res) {

  // user clicks on page 
  console.log("View page click : user: "+req.query.user+" task_id: "+req.query.task+" url: "
	+req.query.docurl+" doc_id: "+req.query.docid+" query_id: "+req.query.queryid);

  if (req.query.user && req.query.docurl && req.query.task && 
	  req.query.queryid && req.query.page && req.query.docid) {
		  
	  database.addClickDoc(req.query.user, req.query.task,
  	  req.query.queryid, req.query.page, req.query.docid, 
  	  req.query.docurl, req.query.time);

  	  // Check if url is on the server.
  	  if (req.query.docurl in global_page_location_dict) 
    	    res.sendFile(__dirname+'/'+global_page_location_dict[req.query.docurl])
  	  else {
  	    // if not load it.
  	    	
  	    options = {
  	      url : req.query.docurl,
  	      headers: {
  	    	"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420.1"+
  	    		"(KHTML, like Gecko) Version/3.0 Mobile/3B48b Safari/419.3"
  	      }
  	    }
  	    request(options, function(error, response, body) {
  	        
  	    	// check if response is success
  	    	if ( response !== undefined && response.statusCode !== 200) 
				  res.send('Response status was ' + response.statusCode);
  	    	var baseUrl= req.query.docurl;
  	    	var to_append = "viewPage?user="+req.query.user+"&task="+req.query.task+
  	    					"&queryid="+req.query.queryid+"&page="+req.query.page+
  	    					"&docid="+req.query.docid+"1&docurl=";
		if (body !== undefined) {
 			$ = cheerio.load(body);
  	    		// Replace all the relative links with absolute page.
  	    		$('[src]').each(function(i, ele) {
  	    			src = $(this).attr('src');
  	    			$(this).attr('src', FullUrl(src, baseUrl, ""));
  	    		});
  	    		$('[srcset]').each(function(i, ele) {
  	    			src = $(this).attr('src');
  	    			$(this).attr('srcset', FullUrl(src, baseUrl,""));
  	    		});
  	    		
  	    		// Replace all the outlinks by modify url function 
  	  		$('a[href]').each(function(i, ele) {
  	    		href = $(this).attr('href');
				// Check if there is no image.
				if(!CheckURLForImage(href) && !CheckURLForDomains(href))
				  $(this).attr('href', FullUrl(href, baseUrl, to_append));
				else
				  $(this).attr('href', FullUrl(href, baseUrl, ""));

  	  		});
		  
  	  		$('link[href]').each(function(i, ele) {
  	    		href = $(this).attr('href');
  	    		$(this).attr('href', FullUrl(href, baseUrl,""));
  	  		});

			$('[background]').each(function(i,ele) {
  	    		href = $(this).attr('background');
  	    		$(this).attr('background', FullUrl(href, baseUrl,""));
			});
			
  	    		// Add the javascript with event detection.
			// $('body').append('<script src="./js/hammer.js"></script>');
			// $('body').append('<script src="./js/hammer_events.js"></script>');
			// $('body').append('<script src="https://code.jquery.com/jquery-1.9.1.min.js"></script>');
  	    		// Save the html to a file.
			var filename = "pages/"+req.query.user+'_'+(saved_pages_count) + ".html";
			saved_pages_count++;
			fs.writeFile(filename, $.html(), function(err) {
					  console.log('Written html to ' + filename);
			});
			global_page_location_dict[req.query.docurl] = filename;
			database.addPageLocation(filename, req.query.docurl, req.query.docid, req.query.time);
			// Add the url mapping to database
			if (!res.headersSent)	
				res.send($.html());
		}
  	    });
  	  }
  } 

});

function CheckURLForDomains(url) {
   return(url.match(/(instagram\.com|viewPage|bleacherreport\.com|facebook\.com|youtube\.com|timesofindia)/) != null);
}

function CheckURLForImage(url) {
   return(url.match(/\.(jpeg|jpg|gif|png)/) != null);
}

function Relative(uri) {
  return !url.parse(uri || '').host;
}

function FullUrl(uri, baseUrl, to_append) {
  full_url =  (uri && Relative(uri)) ? url.resolve(baseUrl, uri) : uri;

  return to_append+full_url; 
}

//-------------------------------------------------------
// START THE SERVER
//-------------------------------------------------------
var port = 4730;
app.listen(port);
console.log('Magic happens on port ' + port);
