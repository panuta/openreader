


function open_publish_modal(uid, callback) {
  if(!$('#publish-publication-modal').length) {
    $('body').append('<div class="modal hide fade" id="publish-publication-modal" style="display:none;"><div class="modal-header"><a class="close" href="#">×</a><h3>ยืนยันการเผยแพร่</h3></div><div class="modal-message"></div><div class="modal-body">ต้องการเผยแพร่ไฟล์นี้ทันที?</div><div class="modal-footer"><input class="btn" type="button" value="ยกเลิก" /><input class="btn primary" type="submit" value="เผยแพร่ทันที" /></div></div>');
    $("#publish-publication-modal").modal({backdrop:'static'});
  }

  $("#publish-publication-modal input[type='submit']").off('click').on('click', function(e) {
    $("#publish-publication-modal .modal-footer input").attr("disabled", true);
    $.post('/publication/publish/', {uid:$("#publish-publication-modal").data('uid')}, function(response) {
      $("#publish-publication-modal .modal-footer input").attr("disabled", false);

      if(response.status == 'error') {
        var message = '';
        if(response.error == 'missing-parameters') {message = 'ขาดข้อมูลที่จำเป็นบางตัว ไม่สามารถประมวลผลได้';}
        if(response.error == 'access-denied') {message = 'คุณไม่สามารถเข้าถึงการทำงานนี้ได้';}
        if(response.error == 'invalid-status') {message = 'ไฟล์ไม่อยู่ในสถานะที่สามารถเผยแพร่ในทันทีได้ หรือไฟล์ถูกเผยแพร่ไปแล้ว';}
        $('#publish-publication-modal .modal-message').html(message).show();

      } else {
        if(callback) {
          if(callback(response, $("#publish-publication-modal").data('uid'))) {
            $("#publish-publication-modal").modal('hide');
          }
        } else {
          window.location.reload();
        }
      }
    }, 'json');

    return false;
  });

  $("#publish-publication-modal input[type='button']").on('click', function(e) {
    $("#publish-publication-modal").modal('hide');
    return false;
  });

  $('#publish-publication-modal .modal-footer').show();
  $('#publish-publication-modal .modal-message').hide();
  $("#publish-publication-modal").modal('show');
  $("#publish-publication-modal").data('uid', uid);
}

function open_unpublish_modal(uid, callback) {
  if(!$('#publish-publication-modal').length) {
    $('body').append('<div class="modal hide fade" id="publish-publication-modal" style="display:none;"><div class="modal-header"><a class="close" href="#">×</a><h3>ยืนยันหยุดการเผยแพร่</h3></div><div class="modal-message"></div><div class="modal-body">ต้องการยืนยันที่จะหยุดการเผยแพร่ไฟล์นี้?</div><div class="modal-footer"><input class="btn" type="button" value="ยกเลิก" /><input class="btn primary" type="submit" value="หยุดการเผยแพร่" /></div></div>');
    $("#publish-publication-modal").modal({backdrop:'static'});
  }

  $("#publish-publication-modal input[type='submit']").off('click').on('click', function(e) {
    $("#publish-publication-modal .modal-footer input").attr("disabled", true);
    $.post('/publication/unpublish/', {uid:$("#publish-publication-modal").data('uid')}, function(response) {
      $("#publish-publication-modal .modal-footer input").attr("disabled", false);

      if(response.status == 'error') {
        var message = '';
        if(response.error == 'missing-parameters') {message = 'ขาดข้อมูลที่จำเป็นบางตัว ไม่สามารถประมวลผลได้';}
        if(response.error == 'access-denied') {message = 'คุณไม่สามารถเข้าถึงการทำงานนี้ได้';}
        if(response.error == 'invalid-status') {message = 'ไฟล์ไม่อยู่ในสถานะที่สามารถเหยุดผยแพร่ในทันทีได้ หรือไฟล์ถูกหยุดเผยแพร่ไปแล้ว';}
        $('#publish-publication-modal .modal-message').html(message).show();

      } else {
        if(callback) {
          if(callback(response, $("#publish-publication-modal").data('uid'))) {
            $("#publish-publication-modal").modal('hide');
          }
        } else {
          window.location.reload();
        }
      }
    }, 'json');

    return false;
  });

  $("#publish-publication-modal input[type='button']").on('click', function(e) {
    $("#publish-publication-modal").modal('hide');
    return false;
  });

  $('#publish-publication-modal .modal-footer').show();
  $('#publish-publication-modal .modal-message').hide();
  $("#publish-publication-modal").modal('show');
  $("#publish-publication-modal").data('uid', uid);
}