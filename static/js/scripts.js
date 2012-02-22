
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

/* DOCUMENTS PAGE
********************************************************/

function increaseAllCount(shelf_id) {
  var count_num = $('.content-sidebar .shelf-all span').text().split(' ')[0].substring(1) * 1;
  count_num = count_num + 1;
  $('.content-sidebar .shelf-all span').text('(' + count_num + ' ไฟล์)');
}

function increaseShelfCount(shelf_id) {
  var count_num = $('#shelf-' + shelf_id + ' span').text().split(' ')[0].substring(1) * 1;
  count_num = count_num + 1;
  $('#shelf-' + shelf_id + ' span').text('(' + count_num + ' ไฟล์)');
}

function initializeDocumentsPage(shelf_id) {
  
  if(shelf_id) {
    
    // ----------- UPLOAD BUTTON -----------
    $('.upload_publication_button').button();
    $('.upload_publication_button').on('click', function(e) {
      $('#upload_dropzone').slideToggle('fast');
    });

    $('#fileupload').fileupload({
      dataType: 'json',
      dropZone: $('#upload_dropzone'),
      url: '/org/' + var_organization_slug + '/documents/shelf/' + shelf_id + '/upload/',
      limitConcurrentUploads: 5,

      add: function (e, data) {
        $('.no_information').remove();
        $('.documents-upload-table').show();

        var file = data.files[0];
        if(file.size > MAX_PUBLICATION_FILE_SIZE) {
          var error_row = $('<tr class="error_row"><td>' + file.name + '<div class="error_message">ไฟล์มีขนาดใหญ่เกินกำหนด (สูงสุดที่ ' + MAX_PUBLICATION_FILE_SIZE_TEXT + ')</div></td><td></td><td class="row_actions"><button class="btn-small danger btn delete_button" >ยกเลิก</button></td></tr>');
          error_row.prependTo('.documents-upload-table tbody');

        } else {
          var uploading_row = $('<tr><td>' + file.name + '</td><td><div class="upload_progressbar"></div></td><td class="row_actions"><button class="btn-small danger btn cancel_button" >ยกเลิก</button></td></tr>');
          uploading_row.find('.upload_progressbar').progressBar({width:262, height:20, boxImage:'/static/libs/progressbar/images/progressbar.png', barImage:{0:'/static/libs/progressbar/images/progressbg.png', 30:'/static/libs/progressbar/images/progressbg.png', 70:'/static/libs/progressbar/images/progressbg.png'}});
          uploading_row.prependTo('.documents-upload-table tbody');

          uploading_row.data('data', data);
          data.context = uploading_row;

          data.submit();
        }
      },
      progress: function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        data.context.find('.upload_progressbar').progressBar(progress);
      },
      done: function (e, data) {
        var file = data.files[0];
        responseObject = data.result;

        if(responseObject.status == 'success') {
          $('.checkbox_actions').show();
          $('.documents-table').show();

          data.context.remove();
          if(!$('.documents-upload-table tbody tr').length) {
            $('.documents-upload-table').hide();
          }

          var uploaded_row = $('<tr id="' + responseObject.uid + '" class="uploaded_row"><td class="row_checkbox"><input type="checkbox" checked="checked"/></td><td class="download"><a href="' + responseObject.download_url + '" title="ดาวน์โหลดไฟล์ ' + responseObject.file_ext.toUpperCase() + '" data-content="ขนาดไฟล์ ' + responseObject.file_size_text + '">ดาวน์โหลดไฟล์</a></td><td class="file"><div class="filename">' + responseObject.title + '</div><div class="uploaded">อัพโหลดเมื่อวันที่ ' + responseObject.uploaded + '</div><div class="tag"><ul></ul></div></td><td class="row_actions"><input type="hidden" name="description" value=""/><input type="hidden" name="thumbnail" value="' + responseObject.thumbnail_url + '"/><button class="btn-small btn edit_publication_button" data-toggle="button">แก้ไข</button></td></tr>');
          uploaded_row.find('.edit_publication_button').button();
          uploaded_row.find('.download a').popover();

          increaseAllCount();
          increaseShelfCount(responseObject.shelf);

          uploaded_row.prependTo('.documents-table tbody');

          $('.checkbox_actions input[type="checkbox"]').attr('checked', true);
          $('.checkbox_actions').addClass('checkbox_actions_selected').find('a').removeClass('disabled');

        } else {
          var error_message = 'เกิดข้อผิดพลาด ไม่สามารถอัพโหลดไฟล์ได้';

          if(responseObject.error == 'file-missing') error_message = 'ไม่สามารถอ่านไฟล์ที่ต้องการอัพโหลดได้';
          if(responseObject.error == 'file-size-exceed') error_message = 'ไฟล์มีขนาดใหญ่เกินกำหนด';
          if(responseObject.error == 'access-denied') error_message = 'ผู้ใช้ไม่สามารถอัพโหลดไฟล์ในชั้นหนังสือนี้ได้';
          if(responseObject.error == 'upload-failed') error_message = 'ไม่สามารถบันทึกไฟล์ที่อัพโหลดได้';

          data.context.addClass('error_row').find('td:first').append('<div class="error_message">' + error_message + '</div>');
          data.context.find('.cancel_button').removeClass('cancel_button').addClass('delete_button');
        }
      },
      fail: function (e, data) {
        if (data.errorThrown == 'abort') {
          data.context.remove();
          if(!$('.documents-upload-table tbody tr').length) $('.documents-upload-table').hide();

        } else {
          data.context.addClass('error_row').find('td:first').append('<div class="error_message">เกิดข้อผิดพลาด ไม่สามารถอัพโหลดไฟล์ได้</div>');
        }
      }
    });

    $(document).bind('drop dragover', function (e) {
      e.preventDefault();
    });

    $('.documents-upload-table .cancel_button').live('click', function(e) {
      var uploading_row = $(this).closest('tr');
      uploading_row.data('data').jqXHR.abort();
    });

    $('.documents-upload-table .delete_button').live('click', function(e) {
      $(this).closest('tr').remove();
      if(!$('.documents-upload-table tbody tr').length) $('.documents-upload-table').hide();
    });
  }

  // ----------- PUBLICATION TABLE -----------

  $('.documents-table .download a').popover();

  // ----------- EDIT PUBLICATION -----------

  $('.edit_publication_button').button();
  $('.edit_publication_button').live('click', function(e) {
    if($(this).hasClass('active')) {
      var rowObject = $(this).closest('tr');
      
      $('.editing_row').remove();
      rowObject.prevAll().find('.edit_publication_button').removeClass('active');
      rowObject.nextAll().find('.edit_publication_button').removeClass('active');

      var uid = rowObject.attr('id');
      var title = rowObject.find('td.file div.filename').text();
      var description = rowObject.find('input[name="description"]').val();
      var thumbnail = rowObject.find('input[name="thumbnail"]').val();
      var tags = rowObject.find('td.file div.tag ul').html();
      
      var editing_row = $('<tr class="editing_row"><td colspan="6"><div class="wrapper" style="display:none;"><div class="cover"><img src="' + thumbnail + '" /></div><!--<div class="original_filename"><em>test.pdf</em> [ <a href="#">เปลี่ยนไฟล์</a> ]</div>--><form><div class="item"><label for="id_name">หัวข้อ</label><div class="input"><input type="text" name="name" value="' + title + '" /></div></div><div class="item"><label for="id_description">คำอธิบาย</label><div class="input"><textarea>' + description + '</textarea></div></div><div class="item"><label for="id_tags">แถบป้าย</label><div class="input"><ul id="edit_tags">' + tags + '</ul></div></div><div class="form_actions"><div class="right_actions"><a href="#" class="link replace_link">เปลี่ยนไฟล์ใหม่</a> | <a href="#delete_confirmation_modal" class="danger delete_link" data-toggle="modal">ลบไฟล์</a></div><button class="btn-primary btn save_button">บันทึกข้อมูล</button><button class="btn cancel_button">ยกเลิก</button></div></form></div></td></tr>');
      editing_row.data('uid', uid);
      editing_row.insertAfter($(this).closest('tr')).show().find('.wrapper').slideDown('fast');

      $('#edit_tags').tagit({tagSource: function(request, response) {
        $.getJSON('/ajax/' + var_organization_slug + '/query/publication-tags/', {
          term: extractLast(request.term)
        }, response);

      }, triggerKeys: ['enter', 'comma', 'tab']});

      editing_row.find('.save_button').on('click', function(e) {
        var title = $('.editing_row input[name="name"]').val();
        var description = $('.editing_row textarea').val();
        var tags = new Array();
        var tag_html = '';

        var editing_tags = $('#edit_tags').tagit('tags');
        for(var i=0; i<editing_tags.length; i++) {
          tags.push(editing_tags[i].label);
          tag_html = tag_html + '<li>' + editing_tags[i].label + '</li>';
        }

        $.post('/ajax/' + var_organization_slug + '/publication/edit/', {uid:uid, title:title, description:description, tags:tags}, function(response) {
          if(response.status == 'success') {
            rowObject.find('td.file div.filename').text(title);
            rowObject.find('input[name="description"]').val(description);
            rowObject.find('td.file div.tag ul').html(tag_html);

            rowObject.css('backgroundColor', '#99cc99');
            rowObject.animate({backgroundColor:"#FFFFFF"}, 1500);

            $('.edit_publication_button').removeClass('active');
            $('.editing_row .wrapper').slideUp('fast', function() {
              $(this).closest('tr').remove();
            });

          } else {
            if(response.error == 'invalid-publication') {
              $('#message_modal').modal('show').find('.modal-body p').text('ข้อมูลไม่ถูกต้อง');
            }

            if(response.error == 'missing-parameter') {
              $('#message_modal').modal('show').find('.modal-body p').text('ข้อมูลไม่ครบถ้วน');
            }
          }
        }, 'json');

        return false;
      });

      editing_row.find('.form_actions .cancel_button').on('click', function(e) {
        $('.edit_publication_button').removeClass('active');
        $('.editing_row .wrapper').slideUp('fast', function() {
          $(this).closest('tr').remove();
        });

        return false;
      });

      editing_row.find('.replace_link').on('click', function(e) {
        $('#replace_publication_modal').modal('show');
        $('#replace_publication_modal .replace_file_input').fileupload('option', 'url', '/publication/' + uid + '/replace/');

        return false;
      });

    } else {
      $('.editing_row .wrapper').slideUp('fast', function() {
        $(this).closest('tr').remove();
      });
    }

    return false;
  });

  // ----------- REPLACE PUBLICATION -----------

  $('#replace_publication_modal .replace_file_input').fileupload({
    dataType: 'json',
    add: function (e, data) {
      var file = data.files[0];
      if(file.size > MAX_PUBLICATION_FILE_SIZE) {
        $('#replace_publication_modal .modal-message').remove();
        $('#replace_publication_modal .modal-header').after('<div class="modal-message">ไฟล์มีขนาดใหญ่เกินกำหนด (สูงสุดที่ ' + MAX_PUBLICATION_FILE_SIZE_TEXT + ')</div>');

      } else {
        var uid = $('.editing_row').data('uid');
        var rowObject = $('#' + uid);
        
        rowObject.find('.uploaded').hide().after('<div class="upload_progressbar"></div>');
        rowObject.find('.upload_progressbar').progressBar({width:262, height:20, boxImage:'/static/libs/progressbar/images/progressbar.png', barImage:{0:'/static/libs/progressbar/images/progressbg.png', 30:'/static/libs/progressbar/images/progressbg.png', 70:'/static/libs/progressbar/images/progressbg.png'}});

        //rowObject.data('data', data);
        data.rowObject = rowObject;
        data.submit();

        $('#replace_publication_modal').modal('hide');
        
        $('tr.editing_row').remove();
        rowObject.find('.edit_publication_button').removeClass('active').hide();
        rowObject.find('.row_actions').append('<button class="btn btn-danger cancel_button">ยกเลิก</button>');

        rowObject.find('.cancel_button').on('click', function(e) {
          //var context = $(this).closest('tr');
          //context.data('data').jqXHR.abort();
          data.jqXHR.abort();
        });
      }
    },
    progress: function (e, data) {
      var progress = parseInt(data.loaded / data.total * 100, 10);
      data.rowObject.find('.upload_progressbar').progressBar(progress);
    },
    done: function (e, data) {
      var file = data.files[0];
      responseObject = data.result;

      if(responseObject.status == 'success') {
        data.rowObject.find('.uploaded').html('อัพโหลดเมื่อวันที่ ' + responseObject.uploaded + ' (เปลี่ยนไฟล์เมื่อวันที่ ' + responseObject.replaced + ')').show();
        data.rowObject.attr('id', responseObject.uid);
        data.rowObject.find('.download a')
          .attr('href', responseObject.download_url)
          .attr('data-original-title', 'ดาวน์โหลดไฟล์ ' + responseObject.file_ext.toUpperCase())
          .attr('title', 'ดาวน์โหลดไฟล์ ' + responseObject.file_ext.toUpperCase())
          .attr('data-content', 'ขนาดไฟล์ ' + responseObject.file_size_text);
        data.rowObject.find('input[name="thumbnail"]').val(responseObject.thumbnail_url);

      } else {
        var error_message = 'เกิดข้อผิดพลาด ไม่สามารถอัพโหลดไฟล์ได้';

        if(responseObject.error == 'file-missing') error_message = 'ไม่สามารถอ่านไฟล์ที่ต้องการอัพโหลดได้';
        if(responseObject.error == 'file-size-exceed') error_message = 'ไฟล์มีขนาดใหญ่เกินกำหนด';
        if(responseObject.error == 'access-denied') error_message = 'ผู้ใช้ไม่สามารถอัพโหลดไฟล์ในชั้นหนังสือนี้ได้';

        data.rowObject.find('.uploaded').after('<div class="error_message">' + error_message + '</div>');
      }

      data.rowObject.find('.upload_progressbar').remove();
      data.rowObject.find('.cancel_button').remove();
      data.rowObject.find('.edit_publication_button').show();

    },
    fail: function (e, data) {
      if (data.errorThrown == 'abort') {
        data.rowObject.find('.upload_progressbar').remove();
        data.rowObject.find('.uploaded').show();

      } else {
        data.rowObject.find('.uploaded').after('<div class="error_message">เกิดข้อผิดพลาด ไม่สามารถอัพโหลดไฟล์ได้</div>');
      }
    }
  });

  // ----------- DELETE PUBLICATION -----------

  $('#delete_confirmation_modal button[type="submit"]').on('click', function(e) {
    var uid = $('.editing_row').data('uid');

    $.post('/ajax/' + var_organization_slug + '/publication/delete/', {uid:uid}, function(response) {
      $('#delete_confirmation_modal').modal('hide');
      $('.editing_row').remove();

      $('#' + uid).fadeOut('fast', function(e) {
        $(this).remove();

        if(!$('.documents-table input[type="checkbox"]:checked').length) {
          $('.checkbox_actions').removeClass('checkbox_actions_selected').find('a').addClass('disabled');
          $('.checkbox_actions input[type="checkbox"]').attr('checked', false);
        }
      });
    });
    return false;
  });

  // ----------- CHECKBOX ACTIONS -----------

  // Table Checkbox

  $('.checkbox_actions input[type="checkbox"]').on('click', function(e) {
    if($(this).attr('checked')) {
      $('.documents-table input[type="checkbox"]').attr('checked', true);
      $('.documents-table tr').addClass('checked');
      $('.checkbox_actions').addClass('checkbox_actions_selected').find('a').removeClass('disabled');
    } else {
      $('.documents-table input[type="checkbox"]').attr('checked', false);
      $('.documents-table tr').removeClass('checked');
      $('.checkbox_actions').removeClass('checkbox_actions_selected').find('a').addClass('disabled');
    }
  });

  $('.documents-table input[type="checkbox"]').live('click', function(e) {
    if($(this).attr('checked')) {
      $(this).closest('tr').addClass('checked');
    } else {
      $(this).closest('tr').removeClass('checked');
    }

    var checkbox_num = $('.documents-table input[type="checkbox"]:checked').length;
    if(checkbox_num) {
      $('.checkbox_actions').addClass('checkbox_actions_selected').find('input[type="checkbox"]').attr('checked', true);
      $('.checkbox_actions a').removeClass('disabled');
    } else {
      $('.checkbox_actions').removeClass('checkbox_actions_selected').find('input[type="checkbox"]').attr('checked', false);
      $('.checkbox_actions a').addClass('disabled');
    }

    var row_num = $('.documents-table tr').length;
    if(row_num == checkbox_num) {
      $('.checkbox_actions input[type="checkbox"]').attr('checked', true);
    } else {
      $('.checkbox_actions input[type="checkbox"]').attr('checked', false);
    }
  });

  // Checkbox Actions

  $('#add_tag_modal .modal-footer button.btn-primary').on('click', function(e) {
    var tag_name = $('#add_tag_modal .modal-body input[name="tag"]').val();
    var publications = Array();

    $('.documents-table input[type="checkbox"]:checked').each(function(e) {
      publications.push($(this).closest('tr').attr('id'));
    });

    if(tag_name) {
      $.post('{% url ajax_add_publications_tag organization.slug %}', {tag:tag_name, publication:publications}, function(response) {
        if(response.status == 'success') {
          $('.documents-table input[type="checkbox"]:checked').each(function(e) {
            $(this).closest('tr').find('.tag ul').append('<li>' + tag_name + '</li>')
          });
          $('#add_tag_modal').modal('hide');
        
        } else {
          if(response.error == 'missing-parameter') {
            $('#add_tag_modal .modal-header').after('<div class="modal-message">ข้อมูลไม่เพียงพอที่จะเพิ่มแถบป้าย</div>');
          } else if(response.error == 'invalid-publication') {
            $('#add_tag_modal .modal-header').after('<div class="modal-message">ไม่พบไฟล์ที่ต้องการเพิ่มแถบป้ายในระบบ</div>');
          }

        }
      }, 'json');
    }
  });

  $('#add_tag_modal').on('show', function() {
    $('#add_tag_modal .modal-body input[name="tag"]').val('');
  });

  $('#delete_files_confirmation_modal .modal-footer button.btn-danger').on('click', function(e) {
    var publications = new Array();

    $('.documents-table input[type="checkbox"]:checked').each(function(e) {
      publications.push($(this).closest('tr').attr('id'));
    });
    
    $.post('/ajax/' + var_organization_slug + '/publication/delete/', {uid:publications}, function(response) {
      $('#delete_files_confirmation_modal').modal('hide');

      if(response.status == 'success') {
        $('.documents-table input[type="checkbox"]:checked').each(function(e) {
          $(this).closest('tr').remove();
        });

        $('.checkbox_actions input[type="checkbox"]').attr('checked', false);
        $('.checkbox_actions').removeClass('checkbox_actions_selected').find('a').addClass('disabled');

      
      } else {
        if(response.error == 'invalid-publication') {
          $('#message_modal').modal('show').find('.modal-body p').text('ไม่พบไฟล์ที่ต้องการลบในระบบ');
        }
      }
    }, 'json');
  });

  $('#delete_files_confirmation_modal').on('show', function() {
    $('#delete_files_confirmation_modal .modal-footer span').text($('.documents-table input[type="checkbox"]:checked').length);
  });
}
