$( document ).ready(function() {
    function progressHandlingFunction(e){
	if(e.lengthComputable){
            $('#progress').attr({value:e.loaded, max:e.total});
	}
    };
    function before(e)
    {
	$('#progress').show();
	$('#formMeta').hide();

    };
    function success(data)
    {
	window.location = '/video/' + data['id'];
    };

    $("#goUpload").click(function(){
	var title = $('#title').val();
	var description = $('#description').val();
	var route = $('#formMeta').attr('action');
	var formData = new FormData($('#formMeta')[0]);

	$.ajax({
	    url: route,
	    type: 'POST',
	    xhr: function() {
		var myXhr = $.ajaxSettings.xhr();
		if(myXhr.upload){
		    myXhr.upload.addEventListener('progress' ,progressHandlingFunction, false);
		}
		return myXhr;
	    },
	    beforeSend: before,
	    success: success,
	    data: formData,
	    cache: false,
	    contentType: false,
	    processData: false
	});

    });

});
