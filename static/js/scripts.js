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

  /* Publish */
  $('.publication_outstandings .action-publish').on('click', function(e) {
    if(!$('#publish-publication-modal').length) {
      $('body').append('<div class="modal hide fade" id="publish-publication-modal" style="display:none;"><div class="modal-header"><a class="close" href="#">×</a><h3>Publish confirmation</h3></div><div class="modal-body">Publish this publication now?</div><div class="modal-footer"><input class="btn" type="button" value="Cancel" /><input class="btn primary" type="submit" value="Publish Now" /></div></div>');
      $("#publish-publication-modal").modal({backdrop:'static'});

      $("#publish-publication-modal input[type='submit']").on('click', function(e) {
        $("#publish-publication-modal .modal-footer input").attr("disabled", "disabled");
        $.post($("#publish-publication-modal").data('url'), function(response) {
          if(response.error) {
            var message = '';
            if(response.error == 'published') {message = 'This publication is already published';}
            $('#publish-publication-modal .modal-body').append('<div class="error_message">' + message + '</div>');
          } else {
            window.location.reload();
          }
        });

        return false;
      });

      $("#publish-publication-modal input[type='button']").on('click', function(e) {
        $("#publish-publication-modal").modal('hide');
        return false;
      });
    }

    $('#publish-publication-modal .modal-body .error_message').remove();
    $("#publish-publication-modal").modal('show');
    $("#publish-publication-modal").data('url', $(this).attr('href'));
    
    return false;
  });

  /* Schedule */
  $('.publication_outstandings .action-schedule').on('click', function(e) {
    if(!$('#schedule-publication-modal').length) {
      $('body').append('<div class="modal hide fade" id="schedule-publication-modal" style="display:none;"><div class="modal-header"><a class="close" href="#">×</a><h3>Publish schedule</h3></div><div class="modal-body"><div class="schedule_date">วันที่ <span class="yui_date_picker_panel"><button class="yui_date_picker" id="id_schedule_date">Select date</button><input type="hidden" id="id_schedule_date_value" value="" name="schedule_date"><input type="text" class="yui_date_picker_textbox" id="id_schedule_date_display" value=""></span></div><div class="schedule_time">เวลา <select id="id_schedule_time_hour" name="schedule_time_hour"><option></option><option value="0">00</option><option value="1">01</option><option value="2">02</option><option value="3">03</option><option value="4">04</option><option value="5">05</option><option value="6">06</option><option value="7">07</option><option value="8">08</option><option value="9">09</option><option value="10">10</option><option value="11">11</option><option value="12">12</option><option value="13">13</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="17">17</option><option value="18">18</option><option value="19">19</option><option value="20">20</option><option value="21">21</option><option value="22">22</option><option value="23">23</option></select>:<select id="id_schedule_time_minute" name="schedule_time_minute"><option></option><option value="0">00</option><option value="15">15</option><option value="30">30</option><option value="45">45</option></select> น.</div></div><div class="modal-footer"><input class="btn" type="button" value="Cancel" /><input class="btn primary" type="submit" value="Schedule" /></div></div>');
      $("#schedule-publication-modal").modal({backdrop:'static'});

      /* YUI Calendar */
      initializeYUICalendar();
      var date_pickers = YAHOO.util.Dom.getElementsByClassName('yui_date_picker');
      
      for(var i=0; i<date_pickers.length; i++) {
        YAHOO.util.Event.on(date_pickers[i], "click", function(e) {
          e.preventDefault();
          activeCalendarInputID = e.target.id;
          triggerYUICalendar();
        });
      }
      
      $(".yui_date_picker_textbox").click(function(e) {
        activeCalendarInputID = $(this).parent().find(".yui_date_picker").attr('id');
        triggerYUICalendar();
      });

      $("#schedule-publication-modal input[type='submit']").on('click', function(e) {
        $("#schedule-publication-modal .modal-footer input").attr("disabled", "disabled");

        var schedule_date = $('#schedule-publication-modal .schedule_date input[name="schedule_date"]').val();
        var schedule_time_hour = $('#schedule-publication-modal [name="schedule_time_hour"] option:selected').val();
        var schedule_time_minute = $('#schedule-publication-modal [name="schedule_time_minute"] option:selected').val();
        var schedule_time = schedule_time_hour + ':' + schedule_time_minute;

        if(schedule_date && schedule_time_hour && schedule_time_minute) {
          $.post($("#schedule-publication-modal").data('url'), {schedule_date:schedule_date, schedule_time:schedule_time}, function(response) {
            if(response.error) {
              var message = '';
              if(response.error == 'invalid') {message = 'Schedule input is invalid';}
              $('#publish-publication-modal .modal-body').append('<div class="error_message">' + message + '</div>');
            } else {
              window.location.reload();
            }
          });
        }

        return false;
      });

      $("#schedule-publication-modal input[type='button']").on('click', function(e) {
        $("#schedule-publication-modal").modal('hide');
        return false;
      });
    }

    $('#schedule-publication-modal .modal-body .error_message').remove();
    $("#schedule-publication-modal").modal('show');
    $("#schedule-publication-modal").data('url', $(this).attr('href'));
    
    return false;
  });

  /* Cancel Schedule */
  $('.publication_outstandings .action-cancel-schedule').on('click', function(e) {
    if(!$('#cancel-schedule-publication-modal').length) {
      $('body').append('<div class="modal hide fade" id="cancel-schedule-publication-modal" style="display:none;"><div class="modal-header"><a class="close" href="#">×</a><h3>Cancel confirmation</h3></div><div class="modal-body">Do you really want to cancel schedule?</div><div class="modal-footer"><input class="btn" type="button" value="No, do not cancel" /><input class="btn primary" type="submit" value="Yes, cancel schedule" /></div></div>');
      $("#cancel-schedule-publication-modal").modal({backdrop:'static'});

      $("#cancel-schedule-publication-modal input[type='submit']").on('click', function(e) {
        $("#cancel-schedule-publication-modal .modal-footer input").attr("disabled", "disabled");
        $.post($("#cancel-schedule-publication-modal").data('url'), function(response) {
          if(response.error) {
            var message = '';
            if(response.error == 'no-schedule') {message = 'This publication has no schedule';}
            $('#cancel-schedule-publication-modal .modal-body').append('<div class="error_message">' + message + '</div>');
          } else {
            window.location.reload();
          }
        });

        return false;
      });

      $("#cancel-schedule-publication-modal input[type='button']").on('click', function(e) {
        $("#cancel-schedule-publication-modal").modal('hide');
        return false;
      });
    }

    $('#cancel-schedule-publication-modal .modal-body .error_message').remove();
    $("#cancel-schedule-publication-modal").modal('show');
    $("#cancel-schedule-publication-modal").data('url', $(this).attr('href'));
    
    return false;
  });
}


$(document).ready(function () {


})