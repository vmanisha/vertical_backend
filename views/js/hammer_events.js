var body = document.getElementById('search_results');
// Check if it is a search result page.
if (body == null) 
	body = document.getElementById('body');

// Ripped from http://crystal.exp.sis.pitt.edu:8080/cdmobile/ 
// We do not know what the page is
var hammer_body = new Hammer(body);
hammer_body.on("hold tap dragup dragdown dragleft dragright pinchin pinchout doubletap release", function(devent) {
	var type = devent.type;
	var timestamp = devent.gesture.timeStamp;
	var numberoftouches = devent.gesture.touches.length;
	var centerX = Math.round(devent.gesture.center.pageX,-3);
	var centerY = Math.round(devent.gesture.center.pageY,-3);
	var deltaTime = devent.gesture.deltaTime;
	var deltaX = Math.round(devent.gesture.deltaX,-3);
	var deltaY = Math.round(devent.gesture.deltaY,-3);
	var velocityX = Math.round(devent.gesture.velocityX,-3);
	var velocityY = Math.round(devent.gesture.velocityY,-3);
	var direction = devent.gesture.direction;
	var distance = Math.round(devent.gesture.distance,-3);
	var targetid = devent.gesture.target.id;
	var newtag = targetid+' '+devent.gesture.target.className+' ';

	if(newtag.length == 0) newtag=devent.gesture.target.tagName;
	
	var deventsMeta = type+" "+timestamp+" "+numberoftouches+ centerX+" "+centerY+
					  " "+deltaTime+" "+deltaX+" "+deltaY+" "+velocityX+" "+velocityY+" "
					  +direction+" "+distance+" "+newtag+"::::";
					  
	if(type=='dragright'){
	      $('#dragrightdata').val($('#dragrightdata').val() + deventsMeta);  
	}
	else if(type=='dragleft' ){
	      $('#dragleftdata').val($('#dragleftdata').val() + deventsMeta);	
	}
	else if(type=='dragup'){
	      $('#dragupdata').val($('#dragupdata').val() + deventsMeta);
	}
	else if(type=='dragdown'){
	      $('#dragdowndata').val($('#dragdowndata').val() + deventsMeta);				  
	}
	else if(type=='tap'){
	      $('#tapdata').val($('#tapdata').val() + deventsMeta);
	}
	else if(type=='doubletap'){
	      $('#doubletapdata').val($('#doubletapdata').val() + deventsMeta);	
	}
	else if(type=='pinchin'){
	      $('#pinchindata').val($('#pinchindata').val() + deventsMeta);				  
	}
	else if(type=='pinchout'){
	      $('#pinchoutdata').val($('#pinchoutdata').val() + deventsMeta);				  
	}			
	else if(type=='release'){

		var touchHtml = devent.gesture.target.innerHTML;	
		var dragleftdata = $('#dragleftdata').val();
		var dragrightdata = $('#dragrightdata').val();
		var dragupdata = $('#dragupdata').val();
		var dragdowndata = $('#dragdowndata').val();
		var tapdata = $('#tapdata').val();
		var doubletapdata = $('#doubletapdata').val();
		var pinchindata = $('#pinchindata').val();
		var pinchoutdata = $('#pinchoutdata').val();
		
		var new_data = {};

		if(dragleftdata.trim().length > 0)
			new_data['dragleft']= dragleftdata;
		if(dragrightdata.trim().length > 0) 
			new_data['dragright']= dragrightdata;
		if(dragupdata.trim().length > 0)
			new_data['dragup']= dragupdata;
		if(dragdowndata.trim().length > 0) 
			new_data['dragdown']= dragdowndata;
		if(tapdata.trim().length > 0)
		    new_data['tapdata']=  tapdata;
		if(doubletapdata.trim().length >0)
	    	new_data['doubletapdata']= doubletapdata;
		if(pinchindata.trim().length > 0)
			new_data['pinchindata'] =  pinchindata; 
		if(pinchoutdata.trim().length > 0)
			new_data['pinchoutdata'] = pinchoutdata;

		new_data['touch_html'] = touchHtml ;
					 
		//update actions to the logs				
		UpdateLogs(new_data);

		$('#dragleftdata').val("");
		$('#dragrightdata').val("");
		$('#dragupdata').val("");
		$('#dragdowndata').val("");
		$('#tapdata').val("");
		$('#doubletapdata').val("");
		$('#pinchindata').val("");
		$('#pinchoutdata').val("");
	
	} 
});  


function UpdateLogs(post_dict) {
	// Make an ajax call and submit the data.
	$.ajax ( { url : '/submitPageEvent',
				type :"post",
				contentType: "application/json",
				data : JSON.stringify({"events" : post_dict, "url" :window.location.href }),
				success : function (response) {
				
				},
				error : function(response) {
					alert(response);
				} 
	});

}






