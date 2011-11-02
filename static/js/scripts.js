function initialize() {
  $("#upload-publication-modal").modal({backdrop:'static'});
}

$(document).ready(function () {

/* ********** UPLOAD PUBLICATION ********** */

$('[upload-publication]').bind('click', function(e) {
  $('#upload-publication-form .inputs').show();
  $('#upload-publication-form .uploading').remove();
  $('#upload-publication-form .error_message').remove();
  $('#upload-publication-form .modal-footer').show();
  
  var type = $(this).attr('upload-publication');
  $('#upload-publication-form #id_upload_type').val(type);
  
  if(type == 'periodical') {
    $("#upload-publication-form h3").text('Upload periodical issue');
    $('#upload-publication-form .periodical_inputs').show();
    $('#upload-publication-form .custom_inputs').html('');
  
  } else if(type == 'periodical-issue') {
    $("#upload-publication-form h3").text('Upload periodical issue');
    $('#upload-publication-form .periodical_inputs').hide();
    $('#upload-publication-form .custom_inputs').html('<div class="periodical_name">' + $(this).closest('li').attr('periodical-title') + '</div><input type="hidden" id="id_periodical_id" name="periodical_id" value="' + $(this).closest('li').attr('periodical-id') + '"/>');

  } else if(type == 'book') {
    $("#upload-publication-form h3").text('Upload book');
    $('#upload-publication-form .periodical_inputs').hide();
    $('#upload-publication-form .custom_inputs').html('');

  } else {
    $("#upload-publication-form h3").text('Upload publication');
    $('#upload-publication-form .periodical_inputs').hide();
    $('#upload-publication-form .custom_inputs').html('<div class="clearfix"><label id="id_publication_type">Publication type</label><div class="input"><ul class="inputs-list"><li><label><input type="radio" value="periodical" name="publication_type" checked="true"><span>Magazine</span></label></li><li><label><input type="radio" value="book" name="publication_type"><span>Book</span></label></li></ul></div></div>');
  }

  $("#upload-publication-form #id_periodical option:first").attr('selected', 'selected');
  $("#upload-publication-form #id_publication").val("");
  $("#upload-publication-modal").modal('show');

  return false;
})

var upload_progress_intv;
function startProgressBarUpdate(upload_id) {
  if(upload_progress_intv != 0) clearInterval(upload_progress_intv);
  upload_progress_intv = setInterval(function() {
    $.getJSON("/get_upload_progress?X-Progress-ID=" + upload_id, function(data) {
      if (data == null) {
        $("#upload_progressbar").progressBar(100);
        clearInterval(upload_progress_intv);
        upload_progress_intv = 0;
        return;
      }
      var percentage = Math.floor(100 * parseInt(data.uploaded) / parseInt(data.length));
      $("#upload_progressbar").progressBar(percentage);
    });
  }, 4000);
}

$('#upload-publication-form input[type="submit"]').click(function(e) {
  if(!$('#id_publication').val()) {
    return false;
  }

  if($('#upload-publication-form #id_periodical').is(':visible') && $('#upload-publication-form #id_periodical').val() == '') {
    return false;
  }

  if($('#upload-publication-form input[name="publication_type"]').is(':visible')) {
    $('#upload-publication-form #id_upload_type').val($('#upload-publication-form input[name="publication_type"]:selected').val());
  }

  $('#X-Progress-ID').val(var_publisher_id + '-' + (new Date()).getTime());
  
  var options = {
    dataType: 'json',
    url: $('#upload-publication-form').attr('action'),
    success: function(response) {
      console.log(response);
      if(response.error) {
        var message = '';
        if(response.error == 'publisher-notexist') {message = 'Publisher Not Exist';}
        if(response.error == 'invalid-periodical') {message = 'Periodical Invalid';}
        if(response.error == 'invalid-publication_type') {message = 'Publication Type Invalid';}
        if(response.error == 'upload') {message = 'Upload Error';}
        if(response.error == 'upload-unknown') {message = 'Upload File Type Unknown';}
        if(response.error == 'missing-fields') {message = 'Missing Some Field';}

        $('#upload-publication-form .uploading').hide();

        var retry_url = $('#upload-publication-form').attr('action').replace('ajax/','');
        var type = $('#upload-publication-form #id_upload_type').val();
        retry_url = retry_url + '?type=' + type;
        if(type == 'periodical-issue') {
          retry_url = retry_url + '&periodical=' + $('#upload-publication-form #id_periodical_id').val();
        }

        $('#upload-publication-form .inputs').after('<div class="error_message">' + message + ' <a href="' + retry_url + '">Retry?</a></div>').hide();

      } else {
        $("#upload_progressbar").progressBar(100);
        clearInterval(upload_progress_intv);
        upload_progress_intv = 0;
        window.location = response.next_url;
      }
    }
  };
  $('#upload-publication-form').ajaxSubmit(options);

  $("#upload-publication-form .inputs").hide();
  $('#upload-publication-form .modal-footer').hide();

  $('#upload-publication-form .inputs').after('<div class="uploading">Uploading ...<div id="upload_progressbar"></div></div>');
  $('#upload_progressbar').progressBar({boxImage:'/static/libs/progressbar/images/progressbar.gif', barImage:{0:'/static/libs/progressbar/images/progressbg_red.gif', 30:'/static/libs/progressbar/images/progressbg_orange.gif', 70:'/static/libs/progressbar/images/progressbg_green.gif'}});

  startProgressBarUpdate($('#X-Progress-ID').val());

  return false;
})

})