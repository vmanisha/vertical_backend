var body = document.getElementById('search_results');
// Check if it is a search result page.
alert(body== null);
if (body == null) 
	body = document.getElementById('body');

// Ripped from http://crystal.exp.sis.pitt.edu:8080/cdmobile/ 
// We do not know what the page is
var hammer_body = new Hammer(body);
hammer_body.on("tap swipeup swipedown swipeleft swiperight pinchin pinchout doubletap panup pandown", function(devent) {
	var type = devent.type;
	var timestamp = new Date().getTime();
	var deltaTime = devent.deltaTime;
	var deltaX = Math.round(devent.deltaX,-3);
	var deltaY = Math.round(devent.deltaY,-3);
	var velocityX = Math.round(devent.velocityX,-3);
	var velocityY = Math.round(devent.velocityY,-3);
	var direction = devent.direction;
	var distance = Math.round(devent.distance,-3);
	var targetid = devent.target.id;
	var newtag = targetid+' '+devent.target.className+' ';

	if(newtag.length == 0) newtag=devent.target.tagName;
	
	var deventsMeta = " "+timestamp+" "+deltaTime+" "+deltaX+
					  " "+deltaY+" "+velocityX+" "+velocityY+" "
					  +direction+" "+distance+" "+newtag;
  
	// For taps send the data right away.
	var touchHtml = devent.target.innerHTML;	

	var event_value = {"html" : touchHtml, "prop" : deventsMeta};

	// Make an ajax call and submit the data.
	$.ajax ( { url : '/submitPageEvent',
				type :"post",
				contentType: "application/json",
				data : JSON.stringify({"eventtype" : type ,"eventvalue" : event_value , "url" :window.location.href }),
				success : function (response) {
				
				},
				error : function(response) {
					//alert(response);
				} 
	});
	

});







