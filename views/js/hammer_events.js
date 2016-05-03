var body = document.getElementById('search_results');
 alert(body);
// Check if it is a search result page.
if (body == null) {
	
	body = document.getElementById('body');
} 
// Ripped from http://crystal.exp.sis.pitt.edu:8080/cdmobile/ 
// We do not know what the page is
var hammer_body = new Hammer(body);
hammer_body.on("hold tap dragup dragdown dragleft dragright pinchin pinchout doubletap release", function(devent) {
	var type = devent.type;
	var timestamp = devent.gesture.timeStamp;
	var numberoftouches = devent.gesture.touches.length;
	var pointerType = devent.gesture.pointerType;
	var centerX = devent.gesture.center.pageX;
	var centerY = devent.gesture.center.pageY;
	var deltaTime = devent.gesture.deltaTime;
	var deltaX = devent.gesture.deltaX;
	var deltaY = devent.gesture.deltaY;
	var velocityX = devent.gesture.velocityX;
	var velocityY = devent.gesture.velocityY;
	var angle = devent.gesture.angle;
	var direction = devent.gesture.direction;
	var distance = devent.gesture.distance;
	var targetid = devent.gesture.target.id;
	var newtag = targetid+' '+devent.gesture.target.className+' ';

	var wintop = $(window).scrollTop(), docheight = $(document).height(), winheight = $(window).height();
    var  scrolltrigger = 0.95;
	var percentscroll = (wintop/(docheight-winheight))*100;

	if(newtag.length == 0) newtag=devent.gesture.target.tagName;
	
	var deventsMeta = type+" "+timestamp+" "+numberoftouches+" "+pointerType+" "
	                +centerX+" "+centerY+" "+deltaX+" "+deltaY+" "+velocityX+" "+velocityY+" "
					  +angle+" "+direction+" "+distance+" "+newtag+"::::";
					  
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
		
		var new_data = {'dragleft': dragleftdata , 'dragright' : dragrightdata ,
					    'dragup' : dragupdata , 'dragdown': dragdowndata, 
		                'tapdata' :  tapdata , 'doubletapdata': doubletapdata, 
					    'pinchindata' :  pinchindata , 'pinchoutdata' : pinchoutdata,
					   	'touch_html' : touchHtml , 'percentscroll' : percentscroll };
					 
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






