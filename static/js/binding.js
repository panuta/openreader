





$(document).ready(function () {

/* PUBLISH ACTION - PUBLISH */

if($('[publish-action="publish"]').length) {
  
  $('body').append('<div class="modal hide fade" id="publish-publication-modal" style="display: none;"><div class="modal-header"><a class="close" href="#">×</a><h3>Publish confirmation</h3></div><div class="modal-body">Publish this publication now?</div><div class="modal-footer"><input class="btn" type="button" value="Cancel" /><input class="btn primary" type="submit" value="Publish Now" /></div></div>');
  $("#publish-publication-modal").modal({backdrop:'static'});

  $('[publish-action="publish"]').on('click', function(e) {
    $("#publish-publication-modal").modal('show');
    $("#publish-publication-modal").data('url', $(this).attr('href'));
    
    return false;
  });

  $("#publish-publication-modal input[type='submit']").on('click', function(e) {
    $("#publish-publication-modal .modal-footer input").attr("disabled", "disabled");
    $.post($("#publish-publication-modal").data('url'), function(data) {
      window.location.reload();
    });

    return false;
  });

  $("#publish-publication-modal input[type='button']").on('click', function(e) {
    $("#publish-publication-modal").modal('hide');
    return false;
  });
}



})