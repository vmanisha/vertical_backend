//1. Unique Id for each user.
//2. Build Instructions page. (In the app)
//3. Assign type of topics.
//4. For each topic fetch the starting query. (Maybe the entity itself)
//------------------------------------------------------------------------
//Events
//------------------------------------------------------------------------
//Type
//Click
//Scroll up and down.
//Touch events.
//Scroll left and right (Item based event)
//How much time do they spend on tapping and reading.
//------------------------------------------------------------------------

$(function(){
  
   var user_name = $('#user_name').val();
   var task_id = $('#task_id').val();
   var user_query = $('#search_input').val();
   var search_page_id = $('#search_page_id').val();

   alert('Im here!');

   // Add validation for search request. 
   $('#search_form').validate({
	            rules: {   search_input: { required:true }  },
			    errorPlacement: function(error, element) {
                        error.css("color","red");
                        error.css('text-decoration', 'red');
                        error.appendTo('#'+element.attr("id")+'_error');
                },
                submitHandler: function postForm(validator, form, submit_event) {
                        // Grab the query, user_name and task_id to server.
   						user_name = $('#user_name').val();
   						task_id = $('#task_id').val();
   						user_query = $('#search_input').val();
   						page_id = $('#page_id').val();
						
						$.ajax({url:'api/search',data: JSON.stringify({'task':task_id , 'user':user_name, 
						'page':page_id, 'query':user_query }),
	                    	contentType: "application/json",
                    		type:'post',
                    		success : function(output){
								$('#query_id').val(output["query_id"]);
								// output is a json object containing [ [result_type, {result_info} ] ]
								var rid = 1; 
								var result_block;
								var type;
								for (var i in output["results"]) {
									var $element_block = '';
									rid = i;
									type = output["results"][i][0];
									result_block = output["results"][i][1];
									if (type == 'i')
										$element_block=PrepareImageResult(rid, result_block);
									if (type == 'w')			
										$element_block=PrepareWikiResult(rid, result_block);
									if (type == 'v')			
										$element_block=PrepareVideoResult(rid, result_block);
									if (type == 'o')			
										$element_block=PrepareWebResult(rid, result_block);
									$element_block.appendTo('#search_results');
								}
                    		},
                    		error : function(output)
                    		{
                        		$('#search_form_error').css("color","red");
                        		$('#search_form_error').css('text-decoration', 'bold');
                        		$('#search_form_error').html(output.responseText);
                    		}
             		  });
			  }
	});	

	// Add tap events
	// Add swipe events
	// Add pinch event
	// Add drag event
});

function PrepareVideoResult(rid, result_json)
{
//	<div class = 'video_box'>
//		<div class = 'card'>
//			<div class ='card_top' >
//				<h3 class = 'card_heading'> <a> Boyzone </a> </h3>
//				<span class ='domain'> m.youtube.com/wa... </span>
//			</div>
//			<div class = 'video_bottom'>
//				<div class = 'video_thumbnail'>
//					<a href="external_url" ><span ><img alt="title" src= 'thumbnail'></span></a>
//				</div>
//				<div class = 'video_info' > <span class='time_creation' >Time </span>time </div>
//			</div> 
//		</div>
//	</div> 

	// (Title, time, external_url, display_url, thumbnail_image_source)
	var $card_head = $("<h3>", { "class" : "card_heading"}).append(
			$("<a>",{"href": result_json["external_url"], "html" : result_json["title"]}));
	var $domain = $("<span>",{"class" : "domain", "text":result_json["display_url"]});
	var $card_top = $("<div>" ,{ "class": "card_top"}).append($card_head).append($domain);


	var $time_creation = $("<span>", { "class" : "time_creation", "text" :"Time"});
	var $video_info = $("<div>", { "class" : "video_info"}).append($time_creation).append(result_json["time"]);
	var $video_thumb = $("<div>", { "class": "video_thumbnail", 
									"html" : $("<a>", {"href" :result_json["external_url"],
											 "html" : $("<span>", {
												 "html": $("<img>", { 
													 "alt" : result_json["title"],
													 "src": result_json["thumbnail"]
												 })
											 })
										 })
									 });
	var $video_bottom = $("<div>", { "class": "video_bottom"}).append($video_thumb).append($video_info);
	var $card = $("<div>", { "class" : "card"}).append($card_top).append($video_bottom);
	var $video_elem = $("<div>", { "id" : rid,"class" : "video_box"}).append($card);

	return $video_elem;
}

function PrepareWikiResult()
{
	var html_string = '';
	return html_string;
}
// image_result contains multiple images on a panel. 
function PrepareImageResult(image_json)
{

  //  <div class = 'image_box'>
  //  <div class = 'card'>
  //  <div > Images </div>
  //  
  //  <div class = 'main_gallery js_flickity' id = 'image_search_results' 
  //  	data_flickity_options='{"cellAlign":"left", "contain":true , "prevNextButtons": false,  "pageDots": false, "resize":true}'>
  //  	<div class="gallery_cell">  <a> <img src =
  //  		'../img/40_1resized___HOLI_LB2012_002.jpg  '> </a> </div>
  //  	<div class="gallery_cell"> <img src =
  //  		'../img/friends-anniversary-main.jpg ' > </div>
  //    <div class="gallery-cell"> <img src =
  //  	  '../img/Big-Bang-Fair-2014_1-300x225.jpg ' > </div>
  //    <div class="gallery-cell"> <img src =
  //  	  '../img/11429037_10153397369389813_8239213770649931342_n.jpg '> </div>
  //    <div class="gallery_cell"> <img src =
  //  	  '../img/66e6deb0-9242-11e3-9925-21bc8763600a_IMG_6340.jpg '> </div>
  //  
  //  </div>
  //  </div>
  //  </div>

	var $img_elem;

	var inner_div_array = [];

	// Start by creating inner divs.

	return img_elem;
}

function PrepareOrganicResult(result_json)
{

	// <div class = 'organic_box'>
	// 	<div class = 'card'>
	// 	  <div class = 'card_top'>
	// 		<h3 class = 'card_heading'> <a> BZ20 By Boyzone... </a> </h3>
	// 		<span class ='domain'> m.youtube.com/wa... </span>
	// 	  </div>
	// 	  <div class = 'card_bottom'> 
	// 	  Buy
	// 		  <em>Boyzone</em> Tickets from the Official Ticketmaster UK site. Find
	// 		  <em>Boyzone</em> tour dates, event details, reviews and
	// 		  much&nbsp;...
	// 	  </div>
	// 	</div>
	// </div>

	var html_string = '';
		

	return html_string;
}


