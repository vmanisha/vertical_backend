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

   // Add validation for search request. 
   $('#search_form').validate({
	            rules: {   search_input: { required:true }  },
			    errorPlacement: function(error, element) {
                        error.css("color","red");
                        error.css('text-decoration', 'bold');
                        error.appendTo('#'+element.attr("name")+'_error');
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

								// output is a json object containing [ [result_type, {result_info} ] ]
								var html_strings = [];
								var rid = 1; 
								for (var result_block : output) {
									if (result_block[0] == 'Image')
										html_strings.push(PrepareImageResult(rid, result_block[1]));
									if (result_block[0] == 'Wiki')			
										html_strings.push(PrepareWikiResult(rid, result_block[1]));
									if (result_block[0] == 'Video')			
										html_strings.push(PrepareVideoResult(rid, result_block[1]));
									if (result_block[0] == 'Web')			
										html_strings.push(PrepareWebResult(rid, result_block[1]));
								}
								// Add all the html elements to body.
								$('#search_results').append(html_strings);
							
                    		},
                    		error : function(output)
                    		{
                        		$('#search_form_error').css("color","red");
                        		$('#search_form_error').css('text-decoration', 'bold');
                        		$('#search_form_error').html(output.responseText);
                    		}
             		  });
	});	


	// Add tap events
	// Add swipe events

	// Add 




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
//					<a href="http://m.youtube.com/watch?v=7eul_Vt6SZY" ><span ><img alt="Video for
//						boyzone" src= '../img/download.jpg'></span></a>
//	
//				</div>
//				<div class = 'video_info' > <span class='time_creation' >Time </span> Attributes  </div>
//			</div> 
//		</div>
//	</div> 

	// (Title, duration in milliseconds, external_url, display_url, thumbnail_image_source)

	var video_html = $("<div>", {
							id : rid,
							class : "video_box", 
							
	var div_end_string = '</div>';
	var html_string = "<div class = 'video_box'> <div class = 'card'> <div class ='card_top' >";
	

	return html_string;



}

function PrepareWikiResult()
{

	var html_string = '';


	return html_string;



}

function PrepareImageResult()
{
	var html_string = '';


	return html_string;



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
<div class = 'image_box'>
<div class = 'card'>
<div > Images </div>

<div class = 'main_gallery js_flickity' id = 'image_search_results' 
	data_flickity_options='{"cellAlign":"left", "contain":true , "prevNextButtons": false,  "pageDots": false, "resize":true}'>
	<div class="gallery_cell">  <a> <img src =
		'../img/40_1resized___HOLI_LB2012_002.jpg  '> </a> </div>
	<div class="gallery_cell"> <img src =
		'../img/friends-anniversary-main.jpg ' > </div>
  <div class="gallery-cell"> <img src =
	  '../img/Big-Bang-Fair-2014_1-300x225.jpg ' > </div>
  <div class="gallery-cell"> <img src =
	  '../img/11429037_10153397369389813_8239213770649931342_n.jpg '> </div>
  <div class="gallery_cell"> <img src =
	  '../img/66e6deb0-9242-11e3-9925-21bc8763600a_IMG_6340.jpg '> </div>

</div>
</div>
</div>



