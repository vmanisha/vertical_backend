// TODO (mverma): Set the parameters for first visit.
var express = require('express');
var app = express();
var engines = require('consolidate');
var math = require('mathjs');
var bodyParser = require('body-parser');
var database = require('./database');
var search_manager = require('./search_manager');
var ReadWriteLock = require('rwlock');

// For updating the result type shown to a user.
var lock = new ReadWriteLock();

// Global query_id 
var global_query_id = 0;

// User task completion dictionary
// user_id : [task_id,..,task_id]
var user_task_complete_dict = {};

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
	  "user_query" : JSON.stringify(""), "query_id" : JSON.stringify(1),
	  "results" : JSON.stringify({})
  });
});

//----------------------------------------------
// USER MANAGEMENT
//----------------------------------------------
// Register a user with user name and id. 
app.get('/api/registerUser', function(req, res){

	var task_dict = {};
	var tasks_completed = [];
	var user_name = req.body.user;
	// Check if user already exists in use
	if (user_name in user_task_complete_dict)
		// User has used the app before
		tasks_completed = user_task_complete_dict[user_name];
	else
		// User is visiting the app first time. 
		user_task_complete_dict[user_name] = [];

	// Return the list of tasks not finished. 
	for (var task_id in task_desc_dict)
	{
		if(!(task_id in tasks_completed))
			task_dict[task_id] = [task_desc_dict[task_id]['task_query'],
								  task_desc_dict[task_id]['task_desc']] ;
	}
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
		  // Shift the queue.
		  global_query_id;
		  release();
		});
		release();
	  });

	  console.log('New request '+query_id+' '+query_text+' '+task_id +' '+user_name);
	  // given the task and user query, prepare the search result
  	  // page and render that. Keep the global_query_id in page.
  	  var results = search_manager.searchQuery(user_name, task_id, 
	   query_text, page_number);
	  
	  // Save the search results for future use. 
	  database.addSearchResults(user_name, task_id, query_id, query_text, 
			  page_number, results, new Date().getTime());

	  res.render("index.ejs", { "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify(user_name), 
	  "search_page_id": JSON.stringify(page_number),
	  "user_query" : JSON.stringify(query_text), 
	  "query_id" : JSON.stringify(query_id),
	  'results': JSON.stringify(results)});
  }
  else
	  res.render("index.ejs", { "task_id":JSON.stringify(task_id), 
	  "user_name": JSON.stringify(user_name), 
	  "search_page_id": JSON.stringify(page_number),
	  "user_query" : JSON.stringify(query_text), 
	  "query_id" : JSON.stringify(check_result['query_id']),
	  'results':JSON.stringify(check_result['search_results'])});
});

// Submit serp interaction to db.
app.post('/submitSERPEvent', function(req, res){
  
  database.addSerpEvent(req.body.user, req.body.task,
  req.body.query, req.body.doc, req.body.eventt,req.body.value,
  req.body.dist, new Date().getTime());
  res.json(true);

});

// Submit page interaction to db.
app.post('/submitPageClick', function(req, res){
  database.addClickDoc(req.body.user, req.body.task,
  req.body.query, req.body.doc, req.body.docurl,
  new Date().getTime());
  res.json(true);
});

// Submit page responses (relevance and satisfaction) interaction to db.
app.post('/submitPageResponse', function(req, res){
  

});

// Submit task responses (relevance and satisfaction) interaction to db.
app.post('/submitTaskResponse', function(req, res){
  var response_array = req.body.responses;
  var time;
  for(var i = 0; i < response_array.length;i++) 
  {
	for(var rkey in response_array[i])
	  {
		  time = new Date(time.getTime()+10);
		  database.addTaskResponse(req.body.user, req.body.task,
		  rkey,response_array[i][rkey],time.getTime());
	  }
  }
  res.json(true);

});

//-------------------------------------------------------

//-------------------------------------------------------
// START THE SERVER
//-------------------------------------------------------
var port = 4730;
app.listen(port);
console.log('Magic happens on port ' + port);
