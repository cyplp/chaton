

$( document ).ready(function() {
    function progressHandlingFunction(e){
	console.log(e);
	if(e.lengthComputable){
            $('#progress').attr({value:e.loaded,max:e.total});
	}
    }
    $("#goUpload").click(function(){
	var title = $('#title').val();
	var description = $('#description').val();
	var route = $('#formMeta').attr('action');
	var id = ''
	var formData = new FormData($('#formMeta')[0]);
	$.ajax({
	    url: route,
	    type: 'POST',
	    xhr: function() {  // Custom XMLHttpRequest
		var myXhr = $.ajaxSettings.xhr();
		if(myXhr.upload){ // Check if upload property exists
		    myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
		}
		return myXhr;
	    },
	    //Ajax events
	    //		       beforeSend: beforeSendHandler,
	    //		       success: completeHandler,
	    //		       error: errorHandler,
		       // Form data
	    data: formData,
	    //Options to tell jQuery not to process data or worry about content-type.
	    cache: false,
	    contentType: false,
	    processData: false
	});
	console.log("here 2")

    }
			);

});
