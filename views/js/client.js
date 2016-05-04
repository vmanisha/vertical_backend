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

   // Add validation for search request. 
   $('#search_form').validate({
        rules: {   search_input: { required:true }  },
	    errorPlacement: function(error, element) {
                error.css("color","red");
                error.css('text-decoration', 'red');
                error.appendTo('#'+element.attr("id")+'_error');
        },
        submitHandler: function postForm(validator, form, submit_event) {
				  search_page_id = 1;
				  if ($('#page_nav').length > 0)
					  $('#page_nav').hide();
				  MakeSearchRequestAndServeResults(search_page_id);
     		  }
	});	

	$('#next_page').on('click', function () {
		// Increment the page_id
		search_page_id++;
		$('#page_nav').hide();
		MakeSearchRequestAndServeResults(search_page_id);

	});

	$('#prev_page').on('click',function () {
		// Decrement the page_id
		search_page_id--;
		$('#page_nav').hide();
		MakeSearchRequestAndServeResults(search_page_id);
	});

	// Attach click event to every element
	$('body').on("click", "a", function(a_event) {
		// Get the url, query, page_id, query_id and task_id
		var link = escape($(this).attr("href"));
		var doc_id =$(this).attr("id");

		if (!CheckURLForImage(link) && !CheckURLForDomains(link) && (doc_id.indexOf("page")==-1))
			$(this).attr("href", ModifyUrl(doc_id, link));
		else {
			// register a click
			var send_data = JSON.stringify({ "user" : user_name, "task" : task_id,
						  "page" : search_page_id , "queryid" : $("#query_id").val(), 
						  "docurl" : link, "docid" : doc_id});
			// Submit it to the server if not a prev_page or next_page click 
			if (doc_id.indexOf("aid") > -1)
			{ 
				$.ajax({ url : "submitPageClick", 
					contentType: "application/json",
					type : "post", 
					data : send_data,
					success : function (output) {
					},
					error: function(response){
						$('#search_form_error').html(response.responseText);
					}

				});
			}
		}

	});
});


// Format the url into following form: viewPage?page=page_number&docid=doc_id&url=url
function ModifyUrl(doc_id, url) {
	var modified_url = 'viewPage?page='+search_page_id+"&docid="+doc_id+
		"&queryid="+$("#query_id").val()+"&user="+user_name+"&task="+
		task_id+"&docurl="+url;

return modified_url;
}

function CheckURLForDomains(url) {
   return(url.match(/(instagram\.com|viewPage|bleacherreport\.com|facebook\.com|youtube\.com|timesofindia)/) != null);
}

function CheckURLForImage(url) {
   return(url.match(/\.(jpeg|jpg|gif|png)/) != null);
}

function MakeSearchRequestAndServeResults(request_page_id) {
   
	// Grab the query, user_name and task_id to server.
	var curr_query = $('#search_input').val();

	// Lower case and remove spaces.
	curr_query = curr_query.toLowerCase().trim();

	// Clear the search result page.
	$("#search_results").html('');


	// Create a new form and submit with parameters.
	var $form =  $('<form>', { "action" : "/search" , "method" : "GET"}).append(
		$('<input>',{ "name":"query", "id":"query" , "value" : curr_query  }))
		.append($('<input>',{ "name":"user", "id":"user" , "value" : user_name}))
		.append($('<input>',{ "name":"task", "id":"task" , "value" : task_id  }))
		.append($('<input>',{ "name":"page", "id":"page" , "value" : search_page_id}));
		
		$form.appendTo('body').hide().submit();
}

function RenderPage(request_page_id,  output)
{
	var rid = 1; 
	var result_block;
	var type;
	for (var i in output) {
		var $element_block = '';
		rid = i;
		type = output[i][0];
		result_block = output[i][1];
		if (type == 'i')
			$element_block=PrepareImageResult(rid, result_block);
		if (type == 'w')			
			$element_block=PrepareCompositeResult('w',rid, result_block);
		if (type == 'v')			
			$element_block=PrepareCompositeResult('v',rid, result_block);
		if (type == 'o')			
			$element_block=PrepareOrganicResult(rid, result_block);
		$element_block.appendTo('#search_results');
	}

	// Add next and previous button.
	var $nav_div = $('<div>',{"id" : "page_nav", "class": "page_nav"});
	if (request_page_id > 1)
	  {	$nav_div = $nav_div.append($("<a>", {"href": "#" , "id": 'prev_page', 
			"text" : "<< Prev"}));
	  	$nav_div = $nav_div.append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
	  }
	$nav_div = $nav_div.append($("<a>", {"href": "#" , "id": 'next_page',"text" : " Next >>"}));
	$nav_div.appendTo('body');
  
}


function PrepareCompositeResult(type, rid, result_json)
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
//				 VIDEO <div class = 'video_info' > <span class='time_creation' >Time </span>time </div>
//				 WIKI <div class = 'video_info' > info </div>
//			</div> 
//		</div>
//	</div> 

	// (Title, time, external_url, display_url, thumbnail_image_source)
	var $card_head = $("<h3>", {"id" : "card_head_"+ rid,  "class" : "card_heading"}).append(
			$("<a>",{"href": result_json["external_url"], "id" : "aid_"+rid, 
					"html" : result_json["title"]}));
	var $domain = $("<span>",{"id" : "domain_id_"+ rid, "class" : "domain", "text":result_json["display_url"]});
	var $card_top = $("<div>" ,{"id" : "card_top_id_"+ rid,  "class": "card_top"}).append($card_head).append($domain);


	var $video_info = $("<div>", { "id" : "info_id_"+ rid, "class" : "video_info"});
	if (type == 'v')
	  $video_info = $video_info.append($("<span>", { "class" : "time_creation",
								  "text" :"Time: "})).append(result_json["time"]);
	if (type == 'w')
	  $video_info = $video_info.append(result_json["desc"]);

	var $video_thumb = $("<div>", {"id" : "dthumb_id_"+rid, "class": "video_thumbnail", 
									"html" : $("<a>", {"href" :result_json["external_url"],
											  "id" : "athumb_id_"+rid, 
											 "html" : $("<span>", {"id" : "sthumb_id_"+ rid, 
												 "html": $("<img>", {"id" : "ithumb_id_"+ rid, 
													 "alt" : result_json["title"],
													 "src": result_json["thumbnail"]
												 })
											 })
										 })
									 });
	var $video_bottom = $("<div>", { "id" : "bott_id_"+ rid, "class": "video_bottom"});

	if (result_json["thumbnail"].length == 0)
		$video_bottom = $video_bottom.append($video_info);
	else
		$video_bottom = $video_bottom.append($video_thumb).append($video_info);
	
	var $card = $("<div>", { "id" : "card_id_"+ rid, "class" : "card"}).append($card_top).append($video_bottom);
	var $video_elem = $("<div>", { "id" : "result_id_"+ rid,"class" : "video_box"}).append($card);

	return $video_elem;
}

// image_result contains multiple images on a panel. 
function PrepareImageResult(rid, image_json)
{
   // <div class = 'image_box'>
   // <div class = 'card'>
   // <div > Images </div>
   // 
   // <div class = 'main_gallery js_flickity' id = 'image_search_results' 
   // 	data_flickity_options='{"cellAlign":"left", "contain":true , "prevNextButtons": false,  "pageDots": false, "resize":true}'>
   // 	<div class="gallery_cell">  <a> <img src =
   // 		'../img/40_1resized___HOLI_LB2012_002.jpg  '> </a> </div>
   //   <div class="gallery-cell"> <img src =
   // 	  '../img/11429037_10153397369389813_8239213770649931342_n.jpg '> </div>
   // </div>
   // </div>
   // </div>
	$('<div>',{'class':'gallery'}).appendTo($('#search_results'));
	var $gallery = $('.gallery').flickity (  { initialIndex: 0, pageDots: false, 
		resize:true, prevNextButtons: false,contain:true });

	
	var $card =  $("<div>",{"id" : "card_id_"+ rid,"class": "card"}).append($("<div>", {"text" : "Images"}));
	for(var i in image_json)
	{
		var result_json = image_json[i];
		var $thumbnail =  $("<img>", { "id" : "image_panel_thumb_id_"+rid,  "src" : result_json["thumbnail"]});
		var $gallery_cell = $("<div>",{"class" : "gallery_cell"}).append(
				$("<a>", { "id" : "image_panel_img_"+rid, "href" : result_json["external_url"]}).append($thumbnail));

		$gallery.flickity( 'insert', $gallery_cell, i);
	}
	var $img_elem= $('<div>', {"id" : "result_id_"+rid ,"class" : "image_box" }).append($card.append($gallery));
	return $img_elem;
}

function PrepareOrganicResult(rid, result_json)
{
	// <div class = 'organic_box'>
	// 	<div class = 'card'>
	// 	  <div class = 'card_top'>
	// 		<h3 class = 'card_heading'> <a> BZ20 By Boyzone... </a> </h3>
	// 		<span class ='domain'> m.youtube.com/wa... </span>
	// 	  </div>
	// 	  <div class = 'card_bottom'> text   </div>
	// 	</div>
	// </div>
	// Web : (['o', {"title": "Title", "desc":"description", "display_url": "DisplayUrl", 
	//		"external_url":"Url"}]);
	var $card_head = $("<h3>", {"id" : "card_head_"+ rid, "class" : "card_heading"}).append(
			$("<a>",{"id" : "aid_"+rid,"href": result_json["external_url"], 
				"html" : result_json["title"]}));
	var $domain = $("<span>",{"id" : "domain_id_"+ rid,"class" : "domain", "text":result_json["display_url"]});
	var $card_top = $("<div>" ,{"id" : "card_top_id_"+ rid,  "class": "card_top"}).append($card_head).append($domain);

	var $card_bottom = $("<div>", {"id" : "bott_id_"+ rid, "class" : "card_bottom", "text" : result_json["desc"]});
	var $card = $("<div>", {"id" : "card_id_"+ rid, "class" : "card"}).append($card_top).append($card_bottom);
	var $organic_elem = $("<div>", { "id" : "result_id_"+rid,"class" : "organic_box"}).append($card);
	return $organic_elem;
}


