function initialize() {
  
}

/* http://stackoverflow.com/questions/5100539/django-csrf-check-failing-with-an-ajax-post-request */
$.ajaxSetup({ 
   beforeSend: function(xhr, settings) {
     function getCookie(name) {
       var cookieValue = null;
       if (document.cookie && document.cookie != '') {
         var cookies = document.cookie.split(';');
         for (var i = 0; i < cookies.length; i++) {
           var cookie = jQuery.trim(cookies[i]);
           // Does this cookie string begin with the name we want?
         if (cookie.substring(0, name.length + 1) == (name + '=')) {
           cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
           break;
         }
       }
     }
     return cookieValue;
     }
     if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
       // Only send the token to relative URLs i.e. locally.
       xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
     }
   } 
});

/* ############### UPLOAD PUBLICATION ############### */
var upload_progress_intv;

function open_upload_publication_modal() {
  clear_upload_publication_modal();
  $('#upload-publication-modal').modal('show');
}

function clear_upload_publication_modal() {
  $('#upload-publication-form .inputs option:first').attr('selected', 'selected');
  $('#upload-publication-form .inputs input[type!="hidden"]').val('');
  $('#upload-publication-form .actions input').attr('disabled', false);
}

function bind_upload_publication_modal() {
  $('#upload-publication-modal').modal({backdrop:'static'});
}

function bind_upload_publication_form() {
  $('#upload-publication-form input[type="submit"]').on('click', function(e) {

    /* Validation */
    var is_empty = false;

    $('#upload-publication-form input[type!="hidden"]').each(function() {
      if(!$(this).val()) is_empty = true;
    });

    $('#upload-publication-form option:selected').each(function() {
      if(!$(this).val()) is_empty = true;
    });

    if(is_empty) return false;

    /* Generate upload id */
    $('#X-Progress-ID').val(var_publisher_id + '-' + (new Date()).getTime());

    /* Start upload */
    var options = {
      dataType: 'json',
      url: $('#upload-publication-form').attr('action'),
      success: function(response) {
        if(response.error) {
          var message = '';
          if(response.error == 'publisher-notexist') {message = 'This publisher not exist';}
          if(response.error == 'module-denied') {message = 'Module is not available';}
          if(response.error == 'module-invalid') {message = 'Module is invalid';}
          if(response.error == 'upload') {message = 'Saving file error';}
          if(response.error == 'form-input-invalid') {message = 'Form inputs is missing or invalid';}

          $('#upload-publication-form .uploading').remove();

          $('#upload-publication-form .inputs').after('<div class="error_message">' + message + ' <div><a href="#">Restart?</a></div></div>');
          $('#upload-publication-form .error_message a').one('click', function(e) {
            $('#upload-publication-form .error_message').remove();
            $('#upload-publication-form .inputs').show();
            clear_upload_publication_modal();
            return false;
          });

        } else {
          $("#upload_progressbar").progressBar(100);
          clearInterval(upload_progress_intv);
          upload_progress_intv = 0;
          window.location = response.next_url;
        }
      }
    };
    
    $('#upload-publication-form .inputs').hide();
    $('#upload-publication-form .actions input').attr('disabled', true);

    $('#upload-publication-form').ajaxSubmit(options);

    $('#upload-publication-form .inputs').after('<div class="uploading">Uploading ...<div id="upload_progressbar"></div></div>');
    $('#upload_progressbar').progressBar({boxImage:'/static/libs/progressbar/images/progressbar.gif', barImage:{0:'/static/libs/progressbar/images/progressbg_red.gif', 30:'/static/libs/progressbar/images/progressbg_orange.gif', 70:'/static/libs/progressbar/images/progressbg_green.gif'}});

    var upload_id = $('#X-Progress-ID').val();
    
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

    return false;
  });
}

/* ############### PUBLICATION OUTSTANDINGS BAR ############### */
function bind_publication_outstandings() {
  $('.publication_outstandings .numbers li a').on('click', function(e) {
    var target = $(this).attr("href");
    $('.publication_outstandings ' + target).slideToggle("fast");
    $('.publication_outstandings .list[id!="' + target.substring(1) + '"]').hide();
    return false;
  });

  $('.publication_outstandings .close_list').on('click', function(e) {
    $('.publication_outstandings .list').slideUp("fast");
    return false;
  });
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
  
  if(type == 'magazine') {
    $("#upload-publication-form h3").text('Upload magazine issue');
    $('#upload-publication-form .magazine_inputs').show();
    $('#upload-publication-form .custom_inputs').html('');
  
  } else if(type == 'magazine-issue') {
    $("#upload-publication-form h3").text('Upload magazine issue');
    $('#upload-publication-form .magazine_inputs').hide();
    $('#upload-publication-form .custom_inputs').html('<div class="magazine_name">' + $(this).closest('li').attr('magazine-title') + '</div><input type="hidden" id="id_magazine_id" name="magazine_id" value="' + $(this).closest('li').attr('magazine-id') + '"/>');

  } else if(type == 'book') {
    $("#upload-publication-form h3").text('Upload book');
    $('#upload-publication-form .magazine_inputs').hide();
    $('#upload-publication-form .custom_inputs').html('');

  } else {
    $("#upload-publication-form h3").text('Upload publication');
    $('#upload-publication-form .magazine_inputs').hide();
    $('#upload-publication-form .custom_inputs').html('<div class="clearfix"><label id="id_publication_type">Publication type</label><div class="input"><ul class="inputs-list"><li><label><input type="radio" value="magazine" name="publication_type" checked="true"><span>Magazine</span></label></li><li><label><input type="radio" value="book" name="publication_type"><span>Book</span></label></li></ul></div></div>');
  }

  $("#upload-publication-form #id_magazine option:first").attr('selected', 'selected');
  $("#upload-publication-form #id_publication").val("");
  $("#upload-publication-modal").modal('show');

  return false;
})

/*
$('#upload-publication-form input[type="submit"]').click(function(e) {
  if(!$('#id_publication').val()) {
    return false;
  }

  if($('#upload-publication-form #id_magazine').is(':visible') && $('#upload-publication-form #id_magazine').val() == '') {
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
        if(response.error == 'invalid-magazine') {message = 'Magazine Invalid';}
        if(response.error == 'invalid-publication_type') {message = 'Publication Type Invalid';}
        if(response.error == 'upload') {message = 'Upload Error';}
        if(response.error == 'upload-unknown') {message = 'Upload File Type Unknown';}
        if(response.error == 'missing-fields') {message = 'Missing Some Field';}

        $('#upload-publication-form .uploading').hide();

        var retry_url = $('#upload-publication-form').attr('action').replace('ajax/','');
        var type = $('#upload-publication-form #id_upload_type').val();
        retry_url = retry_url + '?type=' + type;
        if(type == 'magazine-issue') {
          retry_url = retry_url + '&magazine=' + $('#upload-publication-form #id_magazine_id').val();
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
});
*/

/* ********** PUBLISH ACTIONS ********** */


})