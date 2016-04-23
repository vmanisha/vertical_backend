
var express = require('express');
var app = express();
var engines = require('consolidate');
var bodyParser = require('body-parser');
var database = require('./database');
var search_manager = require('./search_manager');
// Task list dictionary
// task_id : [task_pref, task_desc]

// User task completion dictionary
// user_id : [task_id,..,task_id]
var user_task_complete_dict = {};

// Tab seperated file containing task_id, description
// and preferred vertical. 
var task_file = 'task_descriptions.txt';
var task_desc_dict = database.loadTaskIdAndVerticals(task_file);

// Use body parser
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.set('views', __dirname + '/../views');
app.use("/", express.static(__dirname + '/../views'));
app.use("/js", express.static(__dirname + '/../views/js'));
app.use("/css", express.static(__dirname + '/../views/css'));


app.engine('html', engines.mustache);
app.set('view engine', 'html');
app.get('/index', function(req, res) {
  res.type('text/html'); // set content-type
  res.render('instructions.html');
});

//----------------------------------------------
// USER MANAGEMENT
//----------------------------------------------
// Register a user with user name and id. 
app.post('/api/registerUser', function(req, res){

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
			task_dict[task_id] = task_desc_dict[task_id];
	}
	res.json(task_dict);
});

//----------------------------------------------
// SEARCH REQUEST MANAGEMENT
//----------------------------------------------
// Search a query using ms api and present the results. 
app.post('/api/search', function(req, res){
  var task_id = req.body.task;
  var query_text = req.body.query;
  var user_name = req.body.user;

  // update the query database.
  var query_id = database.addUserQuery(user_name,
	  task_id, query_text, new Date().getTime());

  // given the task and user query, prepare the search result
  // page and render that. 
  // Keep the global_query_id in page.
  results = search_manager.searchQuery(user_name, task_id, 
	  task_desc_dict[task_id]['pref_order'], query_text);
  res.json({'query_id':query_id, 'results':results});

});

// Submit serp interaction to db.
app.post('/api/submitSERPEvent', function(req, res){
  
  database.addSerpEvent(req.body.user, req.body.task,
  req.body.query, req.body.doc, req.body.eventt,req.body.value,
  req.body.dist, new Date().getTime());
  res.json(true);

});

// Submit page interaction to db.
app.post('/api/submitPageClick', function(req, res){
  database.addClickDoc(req.body.user, req.body.task,
  req.body.query, req.body.doc, req.body.docurl,
  new Date().getTime());
  res.json(true);
});

// Submit page responses (relevance and satisfaction) interaction to db.
app.post('/api/submitPageResponse', function(req, res){
  

});

// Submit task responses (relevance and satisfaction) interaction to db.
app.post('/api/submitTaskResponse', function(req, res){
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
app.listen(port);
console.log('Magic happens on port ' + port);
