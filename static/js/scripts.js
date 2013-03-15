
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

/*
 Alert functions
 */

function _showAlertBar(message, alert_class, auto_hide) {
    var alertbar = $('<div class="alert hide alert-' + alert_class + '"><p>' + message + '</p></div>');
    if(auto_hide) {
        alertbar.prependTo('.authenticated-container').slideDown('fast').delay(2000).slideUp('fast');
    } else {
        alertbar.prependTo('.authenticated-container').slideDown('fast');
    }
}

function _addModalMessage(modal_id, message, type) {
    $('#' + modal_id + ' .modal-message').remove();

    if(type == 'success') {
        $('#' + modal_id + ' .modal-header').after('<div class="modal-message modal-message-success"><i class="icon-ok-sign icon-white"></i> ' + message + '</div>');
    } else if(type == 'error') {
        $('#' + modal_id + ' .modal-header').after('<div class="modal-message modal-message-error"><i class="icon-exclamation-sign icon-white"></i> ' + message + '</div>');
    }
}

function _removeModalMessage(modal_id) {
    $('#' + modal_id + ' .modal-message').remove();
}

/*
 Publication Modal
 */

$('.js-open-publication').live('click', function() {
    $('#publication-modal').data('uid', $(this).attr('uid'));
    $('#publication-modal').data('title', $(this).attr('title'));
    $('#publication-modal').modal();
    return false;
});

$(document).ready(function () {

    $('#publication-modal').on('show', function() {
        _removeModalMessage('publication-modal');
        $('#publication-modal .modal-body > :not(.publication)').remove();

        var uid = $(this).data('uid');

        if(uid) {
            if($(this).data('title')) {
                $(this).find('.modal-header h3').text($(this).data('title'));
            } else {
                $(this).find('.modal-header h3').text('เอกสาร');
            }

            $('#publication-modal .modal-body .publication').remove();
            $('#publication-modal .modal-body').html('<div class="panel-message"><i class="loading"></i> '+ gettext('Loading') +'</div>');
            $('#publication-modal .modal-footer .publication').hide();

            $.get('/ajax/publication/' + uid + '/query/', {}, function(response) {
                if(response.status == 'success') {
                    var publication_form = '';
                    if(response.readonly == 'true') {
                        publication_form = $('<div class="publication"><div class="left"><div class="thumbnail"><img src="' + response.thumbnail_url + '" /></div><ul class="file_info"><li>'+ gettext('File') +' <span class="file_ext">' + response.file_ext.toUpperCase() + '</span></li><li>'+ gettext('Size') +' <span class="file_size">' + response.file_size_text + '</span></li></ul></div><div class="right"><form class="publication_form"><div class="control-group"><label class="control-label" for="id_publication_title">'+ gettext('Document title') +'</label><div class="controls"><input type="text" id="id_publication_title" readonly="readonly" value="' + response.title + '"/></div></div><div class="control-group"><label class="control-label" for="id_publication_description">'+ gettext('Description') +'</label><div class="controls"><textarea id="id_publication_description" readonly="readonly">' + response.description + '</textarea></div></div><div class="control-group"><label class="control-label" for="id_publication_tags">'+ gettext('Tags') +'</label><div class="controls"><input type="text" id="id_publication_tags" readonly="readonly" value="' + response.tag_names + '"/></div></div></form></div></div>')
                    } else {
                        publication_form = $('<div class="publication"><div class="left"><div class="thumbnail"><img src="' + response.thumbnail_url + '" /></div><ul class="file_info"><li>'+ gettext('File') +' <span class="file_ext">' + response.file_ext.toUpperCase() + '</span></li><li>'+ gettext('Size') +' <span class="file_size">' + response.file_size_text + '</span></li></ul><div class="actions"><a href="#" class="btn btn-mini replace_button">'+ gettext('Change file') +'</a><a href="#" class="btn btn-mini delete_button">'+ gettext('Delete file') +'</a></div></div><div class="right"><form class="publication_form"><div class="control-group"><label class="control-label" for="id_publication_title">'+ gettext('Document title') +'</label><div class="controls"><input type="text" id="id_publication_title" value="' + response.title + '"/></div></div><div class="control-group"><label class="control-label" for="id_publication_description">'+ gettext('Description') +'</label><div class="controls"><textarea id="id_publication_description">' + response.description + '</textarea></div></div><div class="control-group"><label class="control-label" for="id_publication_tags">'+ gettext('Tags') +'</label><div class="controls"><input type="text" id="id_publication_tags" value="' + response.tag_names + '"/></div></div><div class="control-group"><label class="control-label" for="id_publication_shelves">Shelves</label><div class="controls"><select multiple="multiple" data-placeholder="Select shelves" name="publication_shelves" id="id_publication_shelves">'+ response.shelf_options +'</select></div></div><button class="btn btn-primary save_button"><i class="icon-pencil icon-white"></i> '+ gettext('Save') +'</button></form></div></div>')
                    }

                    $('#publication-modal .modal-header h3').text(response.title);

                    $('#publication-modal .publication .uploaded .uploaded_date').text(response.uploaded);
                    $('#publication-modal .publication .uploaded .uploaded_by').text(response.uploaded_by);
                    $('#publication-modal .publication .download_button').attr('href', response.download_url);

                    $('#publication-modal .panel-message').fadeOut('fast', function() {
                        $('#publication-modal .modal-body').html(publication_form);
                        $('#publication-modal .modal-footer .publication').show();
                    });
                } else {
                    $('#publication-modal .panel-message').remove();
                    $('<div class="panel-message"><i class="icon-exclamation-sign"></i> '+ gettext('File not found') +'</div>').appendTo('#publication-modal .modal-body');
                }
            }, 'json');
        } else {
            $('<div class="message-panel"><i class="icon-exclamation-sign"></i> '+ gettext('File not found') +'</div>').appendTo('#publication-modal .modal-body');
        }
    });

    $('#publication-modal').on('hide', function() {
        $('#publication-modal .right .panel').remove();
        $('#publication-modal .publication_form').show();
    });

    $('#publication-modal').on('panel_hide', function(e, not_remove_message) {
        $('#publication-modal .panel').remove();
        $('#publication-modal .publication_form').show();

        if(!not_remove_message) {
            _removeModalMessage('publication-modal');
        }
    });

    $('#publication-modal .replace_button').live('click', function() {
        $('#publication-modal .publication_form').fadeOut('fast', function() {
            $('#publication-modal .right .panel').remove();
            $('#publication-modal .right').append('<form class="replace_form panel"><label for="replace_file_input">'+ gettext('Choose file to replace') +'</label><input type="file" id="replace_file_input" /><div class="actions"><button class="btn cancel_button">'+ gettext('Cancel') +'</button></div></form>');

            $('#publication-modal .replace_form .cancel_button').on('click', function() {
                $('#publication-modal .panel').fadeOut('fast', function(){
                    $('#publication-modal').trigger('panel_hide');
                });
                return false;
            });

            $('#replace_file_input').fileupload({
                dataType: 'json',
                url: '/org/' + var_organization_slug + '/documents/replace/',
                formData: function (form) {
                    return [{name:"publication_id", value:$('#publication-modal').data('uid')}];
                },
                add: function (e, data) {
                    var file = data.files[0];
                    if(file.size > MAX_PUBLICATION_FILE_SIZE) {
                        _addModalMessage('publication-modal', gettext('File is exceed limitation') +' (' + gettext('max') + ' ' + MAX_PUBLICATION_FILE_SIZE_TEXT + ')', 'error');

                    } else {
                        var uid = $('#publication-modal').data('uid');
                        $('#publication-modal .right .panel').html('<div class="uploading"><div class="upload_progressbar"></div><button class="btn">' + gettext('Cancel') + '</button></div>');
                        $('#publication-modal .right .panel .upload_progressbar').progressBar({width:262, height:20, boxImage:'/static/libs/progressbar/images/progressbar.png', barImage:{0:'/static/libs/progressbar/images/progressbg.png', 30:'/static/libs/progressbar/images/progressbg.png', 70:'/static/libs/progressbar/images/progressbg.png'}});

                        data.submit();

                        $('#publication-modal .right .panel button').on('click', function() {
                            data.jqXHR.abort();
                            $('#publication-modal').trigger('panel_hide');
                        });
                    }
                },
                progress: function (e, data) {
                    var progress = parseInt(data.loaded / data.total * 100, 10);
                    $('#publication-modal .right .panel .upload_progressbar').progressBar(progress);
                },
                done: function (e, data) {
                    var file = data.files[0];
                    var response = data.result;

                    if(response.status == 'success') {
                        $('#publication-modal .file_ext').text(response.file_ext);
                        $('#publication-modal .file_size').text(response.file_size);
                        $('#publication-modal .thumbnail img').attr('src', response.thumbnail_url);

                        _addModalMessage('publication-modal', gettext('Replace file successful'), 'success');

                        $('#publication-modal').trigger('panel_hide', ['not_remove_message']);
                        $('#publication-modal').trigger('publication_replaced', [response.uid, response.file_ext, response.file_size]);

                    } else {
                        var error_message = gettext('Cannot upload file');
                        if(responseObject.error == 'file-size-exceed') error_message = gettext('File is exceed limitation');
                        if(responseObject.error == 'access-denied') error_message = gettext('User cannot upload file in this shelf');
                        _addModalMessage('publication-modal', error_message, 'error');
                    }
                },
                fail: function (e, data) {
                    if (data.errorThrown == 'abort') {
                        $('#publication-modal').trigger('panel_hide');
                    } else {
                        _addModalMessage('publication-modal', gettext('Error, cannot upload file'), 'error');
                    }
                }
            });
        });
        return false;
    });

    $('#publication-modal .delete_button').live('click', function() {
        $('#publication-modal .publication_form').fadeOut('fast', function() {
            $('#publication-modal .right .panel').remove();
            $('#publication-modal .right').append('<form class="delete_form panel"><div><button type="submit" class="btn btn-danger submit_delete_button">'+ gettext('Confirm delete file') +'</button><button class="btn cancel_button">'+ gettext('Cancel') +'</button></div></form>');

            $('#publication-modal .delete_form .submit_delete_button').on('click', function() {
                var uid = $('#publication-modal').data('uid');

                $.post('/ajax/' + var_organization_slug + '/publication/delete/', {uid:uid}, function(response) {
                    $('#publication-modal').trigger('publication_deleted', [uid]);
                    $('#publication-modal').modal('hide');
                });

                return false;
            });

            $('#publication-modal .delete_form .cancel_button').on('click', function() {
                $('#publication-modal .panel').fadeOut('fast', function(){
                    $('#publication-modal').trigger('panel_hide');
                });
                return false;
            });
        });
        return false;
    });

    $('#publication-modal .save_button').live('click', function() {
        var uid = $('#publication-modal').data('uid');
        var title = $('#id_publication_title').val();
        var description = $('#id_publication_description').val();
        var tagnames = $('#id_publication_tags').val();
        var shelves = $('#id_publication_shelves').val();

        $.post('/ajax/' + var_organization_slug + '/publication/edit/', {uid:uid, title:title, description:description, tags:tagnames, shelves:shelves}, function(response) {
            if(response.status == 'success') {
                _addModalMessage('publication-modal', gettext('Save successful'), 'success');
                $('#publication-modal').trigger('publication_updated', [uid, title, tagnames]);
            } else {
                var error_message = gettext('Cannot save file');
                if(response.error == 'publication-notfound') error_message = gettext('File not found in system');
                if(response.error == 'parameter-missing') error_message = gettext('Information is not completely');
                _addModalMessage('publication-modal', error_message, 'error');
            }
        }, 'json');
        return false;
    });
});


/* DOCUMENTS PAGE
********************************************************/

function initializeDocumentsPage() {

    // UPLOAD PUBLICATION ----------------------------------------------------------------------------------------------

    $('.js-upload-publication').on('click', function() {
        $('.upload_tool select option:first').attr('selected', true);
        // $('.js-upload-tool-file-input').hide();
        $('.upload_tool').slideToggle('fast');
        return true;
    });

    // $('.js-upload-tool-shelf-input').on('change', function() {
    //     var selected_value = $(this).find('option:selected').val();
    //     if(selected_value) {
    //         $('.js-upload-tool-file-input').show();
    //     } else {
    //         $('.js-upload-tool-file-input').hide();
    //     }
    // });

    $('.js-dismiss-uploading').live('click', function() {
        $(this).closest('li').fadeOut('fast', function() {
            $(this).remove();
        });
        return false;
    });

    $('#id_upload_file').fileupload({
        dataType: 'json',
        url: '/org/' + var_organization_slug + '/documents/upload/',
        limitConcurrentUploads: 5,
        formData: function (form) {
            return [{name:"shelves", value:form.find('select').val()}];
        },
        add: function(e, data) {
            $('.no_shelf').remove();

            var file = data.files[0];
            if(file.size > MAX_PUBLICATION_FILE_SIZE) {
                var error_row = $('<li class="uploading failed"><div class="filename"><em>' + file.name + '</em> ' + gettext('File is exceed limitation') +' (' + gettext('max') + MAX_PUBLICATION_FILE_SIZE_TEXT + ')</div><div><button class="btn btn-small js-dismiss-uploading">'+gettext('Cancel upload file')+'</button></div></li>');
                error_row.prependTo('.js-uploading');

            } else {
                var uploading_row = $('<li class="uploading"><button class="btn btn-small js-cancel-upload">'+gettext('Cancel')+'</button><div class="filename">'+gettext('Uploading')+' <em>' + file.name + '</em></div><div class="upload_progressbar"></div></li>');
                uploading_row.find('.upload_progressbar').progressBar({width:262, height:20, boxImage:'/static/libs/progressbar/images/progressbar.png', barImage:{0:'/static/libs/progressbar/images/progressbg.png', 30:'/static/libs/progressbar/images/progressbg.png', 70:'/static/libs/progressbar/images/progressbg.png'}});
                uploading_row.prependTo('.js-uploading');

                uploading_row.data('data', data);
                data.context = uploading_row;

                data.submit();
            }
        },
        progress: function(e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            data.context.find('.upload_progressbar').progressBar(progress);
        },
        done: function(e, data) {
            var file = data.files[0];
            var responseObject = data.result;

            if(responseObject.status == 'success') {
                data.context.addClass('uploaded').html('<div class="filename"><em>' + file.name + '</em> '+gettext('Uploaded on')+' ' + responseObject.uploaded + '</div><div class="file_title"><button class="btn btn-small js-open-publication" title="' + responseObject.title + '" uid="' + responseObject.uid + '">'+gettext('Edit document')+'</button></div>');

                // Update num of files in shelf
                for(var i=0; i<responseObject.shelves.length; i++){
                    console.log(responseObject.shelves[i]);
                    var file = gettext('files')
                    if( $('#shelf-' + responseObject.shelves[i] + ' .num_files').text() == '0 file' ){
                        file = gettext('file')
                    }
                    $('#shelf-' + responseObject.shelves[i] + ' .num_files').text($('#shelf-' + responseObject.shelves[i] + ' .num_files').text().split(' ')[0] * 1 + 1 + ' ' + file);
                }

                _appendRecentDocuments(responseObject.uid, responseObject.title, responseObject.uploaded);
                
            } else {
                var error_message = gettext('Cannot upload file');

                if(responseObject.error == 'file-size-exceed') error_message = gettext('File is exceed limitation');
                if(responseObject.error == 'access-denied') error_message = gettext('User cannot upload file in this shelf');

                data.context.addClass('failed').html('<div class="filename"><em>' + file.name + '</em> ' + error_message + '</div><div><button class="btn btn-small js-dismiss-uploading">'+gettext('Cancel upload file')+'</button></div>');
            }
        },
        fail: function (e, data) {
            if (data.errorThrown == 'abort') {
                data.context.remove();
            } else {
                var file = data.files[0];
                data.context.addClass('failed').html('<div class="filename"><em>' + file.name + '</em> '+gettext('Error, cannot upload file')+'</div><div><button class="btn btn-small js-dismiss-uploading">'+gettext('Cancel upload file')+'</button></div>');
            }
        }
    });

    $('.js-cancel-upload').live('click', function() {
        var uploading_row = $(this).closest('li');
        uploading_row.data('data').jqXHR.abort();

        $(this).closest('li').fadeOut('fast', function() {
            $(this).remove();
        });
        return false;
    });

    function _appendRecentDocuments(uid, title, uploaded) {
        $('.documents_sidebar .no_recent').remove();
        if(!$('.documents_sidebar ul').length) {
            $('.documents_sidebar h3').after('<ul></ul>');
        }

        $('.documents_sidebar ul').prepend('<li><div><a href="#" class="js-open-publication" title="' + title + '" uid="' + uid + '">' + title + '</a></div><div class="uploaded">'+gettext('Uploaded on')+' ' + uploaded + '</div></li>');
    }

    // PUBLICATION MODAL -----------------------------------------------------------------------------------------------

    $('#publication-modal').on('publication_updated', function(e, uid, title, tags) {
        $('.documents_sidebar .js-open-publication[uid="' + uid + '"]').attr('title', title).text(title);
    });

    $('#publication-modal').on('publication_deleted', function(e, uid) {
        $.get('/ajax/' + var_organization_slug + '/query/shelves/', {}, function(response) {
            if(response.status == 'success') {
                for(var i=0; i<response.shelves.length; i++) {
                    var shelf = response.shelves[i];
                    $('#shelf-' + shelf.id + ' .num_files').text(shelf.document_count + ' '+ gettext('file'));
                }
            }
        }, 'json');

        $('.documents_sidebar .js-open-publication[uid="' + uid + '"]').closest('li').remove();
        if(!$('.documents_sidebar .js-open-publication').length) {
            $('.documents_sidebar ul').remove();
            $('.documents_sidebar h3').after('<div class="no_recent">'+gettext('No latest files')+'</div>');
        }
    });
}


function initializeDocumentsShelfPage(shelf_id) {

    // UPLOAD TOOL -----------------------------------------------------------------------------------------------------

    $('.js-upload-publication').on('click', function() {
        // $('.upload_tool select option[value="' + shelf_id + '"]').attr('selected', true);
        $('.upload_tool').slideToggle('fast');
        return true;
    });

    $('.js-upload-tool-shelf-input').on('change', function() {
        var selected_value = $(this).find('option:selected').val();
        if(selected_value) {
            $('.js-upload-tool-file-input').show();
        } else {
            $('.js-upload-tool-file-input').hide();
        }
    });

    $('.js-dismiss-uploading').live('click', function() {
        $(this).closest('li').fadeOut('fast', function() {
            $(this).remove();
        });
        return false;
    });

    $('#id_upload_file').fileupload({
        dataType: 'json',
        url: '/org/' + var_organization_slug + '/documents/upload/',
        limitConcurrentUploads: 5,
        dropZone: $('.upload_tool'),
        formData: function (form) {
            return [{name:"shelves", value:form.find('select').val()}];
        },
        add: function(e, data) {
            var file = data.files[0];
            if(file.size > MAX_PUBLICATION_FILE_SIZE) {
                var error_row = $('<li class="uploading failed"><div class="filename"><em>' + file.name + '</em> ' + gettext('File is exceed limitation') +' (' + gettext('max') + MAX_PUBLICATION_FILE_SIZE_TEXT + ')</div><div><button class="btn btn-small js-dismiss-uploading">' + gettext('Cancel upload file') +'</button></div></li>');
                error_row.prependTo('.js-uploading');

            } else {
                var uploading_row = $('<li class="uploading"><button class="btn btn-small js-cancel-upload">' + gettext('Cancel') +'</button><div class="filename">' + gettext('Uploading') +' <em>' + file.name + '</em></div><div class="upload_progressbar"></div></li>');
                uploading_row.find('.upload_progressbar').progressBar({width:262, height:20, boxImage:'/static/libs/progressbar/images/progressbar.png', barImage:{0:'/static/libs/progressbar/images/progressbg.png', 30:'/static/libs/progressbar/images/progressbg.png', 70:'/static/libs/progressbar/images/progressbg.png'}});
                uploading_row.prependTo('.js-uploading');

                uploading_row.data('data', data);
                data.context = uploading_row;

                data.submit();
            }
        },
        progress: function(e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            data.context.find('.upload_progressbar').progressBar(progress);
        },
        done: function(e, data) {
            if($('.no_publication').length) {
                $('.documents-content').html('<table class="table documents_table"><tbody></tbody></table>');
            }

            var file = data.files[0];
            var responseObject = data.result;

            if(responseObject.status == 'success') {
                $('.checkbox_actions').show();
                $('.documents_table').show();

                data.context.remove();

                var uploaded_row = $('<tr id="' + responseObject.uid + '" class="uploaded_row"><td class="row_checkbox"><input type="checkbox" checked="checked"/></td><td class="download"><a href="' + responseObject.download_url + '" title="' + gettext('Download file') +' ' + responseObject.file_ext.toUpperCase() + '" data-content="' + gettext('File size') +' ' + responseObject.file_size_text + '">' + gettext('Download file') +'</a></td><td class="file"><div class="filename"><a href="#" class="js-open-publication" uid="' + responseObject.uid + '" title="' + responseObject.title + '">' + responseObject.title + '</a></div><div class="uploaded">' + gettext('Uploaded on') +' ' + responseObject.uploaded + '</div><div class="tag"><ul></ul></div></td></tr>');
                uploaded_row.find('.edit_publication_button').button();
                uploaded_row.find('.download a').popover();
                uploaded_row.prependTo('.documents_table tbody');

                $('.checkbox_actions input[type="checkbox"]').attr('checked', true);
                $('.checkbox_actions').addClass('checkbox_actions_selected').find('a').removeClass('disabled');

            } else {
                var error_message = gettext('Cannot upload file');

                if(responseObject.error == 'file-size-exceed') error_message = gettext('File is exceed limitation');
                if(responseObject.error == 'access-denied') error_message = gettext('User cannot upload file in this shelf');

                data.context.addClass('failed').html('<div class="filename"><em>' + file.name + '</em> ' + error_message + '</div><div><button class="btn btn-small js-dismiss-uploading">' + gettext('Cancel upload file') +'</button></div>');
            }
        },
        fail: function (e, data) {
            if (data.errorThrown == 'abort') {
                data.context.remove();
            } else {
                data.context.addClass('failed').html('<div class="filename"><em>' + file.name + '</em> ' + gettext('Error, cannot upload file') +'</div><div><button class="btn btn-small js-dismiss-uploading">' + gettext('Cancel upload file') +'</button></div>');
            }
        }
    });

    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });

    $('.js-cancel-upload').live('click', function() {
        var uploading_row = $(this).closest('li');
        uploading_row.data('data').jqXHR.abort();

        $(this).closest('li').fadeOut('fast', function() {
            $(this).remove();
        });
        return false;
    });

    // Documents Table -------------------------------------------------------------------------------------------------

    $('.documents_table .download a').popover();

    // Table Checkbox --------------------------------------------------------------------------------------------------

    $('.checkbox_actions input[type="checkbox"]').on('click', function(e) {
        if($(this).attr('checked')) {
            $('.documents_table input[type="checkbox"]').attr('checked', true);
            $('.documents_table tr').addClass('checked');
            $('.checkbox_actions').addClass('checkbox_actions_selected').find('a').removeClass('disabled');
        } else {
            $('.documents_table input[type="checkbox"]').attr('checked', false);
            $('.documents_table tr').removeClass('checked');
            $('.checkbox_actions').removeClass('checkbox_actions_selected').find('a').addClass('disabled');
        }
    });

    $('.documents_table input[type="checkbox"]').live('click', function(e) {
        if($(this).attr('checked')) {
            $(this).closest('tr').addClass('checked');
        } else {
            $(this).closest('tr').removeClass('checked');
        }

        var checkbox_num = $('.documents_table input[type="checkbox"]:checked').length;
        if(checkbox_num) {
            $('.checkbox_actions').addClass('checkbox_actions_selected').find('input[type="checkbox"]').attr('checked', true);
            $('.checkbox_actions a').removeClass('disabled');
        } else {
            $('.checkbox_actions').removeClass('checkbox_actions_selected').find('input[type="checkbox"]').attr('checked', false);
            $('.checkbox_actions a').addClass('disabled');
        }

        var row_num = $('.documents_table tr').length;
        if(row_num == checkbox_num) {
            $('.checkbox_actions input[type="checkbox"]').attr('checked', true);
        } else {
            $('.checkbox_actions input[type="checkbox"]').attr('checked', false);
        }
    });

    // Add Tags Modal --------------------------------------------------------------------------------------------------

    $('#add-tags-modal').on('show', function() {
        if(!$('.documents_table input[type="checkbox"]:checked').length) {
            return false;
        }

        $('#add-tags-modal .modal-body input[name="tag"]').val('');
    });

    $('#add-tags-modal .modal-footer button.btn-primary').on('click', function(e) {
        var tags = $('#add-tags-modal .modal-body input[name="tag"]').val();
        var publications = Array();

        $('.documents_table input[type="checkbox"]:checked').each(function(e) {
            publications.push($(this).closest('tr').attr('id'));
        });

        if(tags) {
            $.post('/ajax/' + var_organization_slug + '/publication/tag/add/', {tags:tags, publication:publications}, function(response) {
                if(response.status == 'success') {
                    for(var i=0; i<publications.length; i++){
                        for(var j=0; j<response.tag_names.length; j++) {
                            if(!$('#' + publications[i] + ' .tag li').filter(function(index){return $(this).text() == response.tag_names[j];}).length) {
                                $('#' + publications[i] + ' .tag ul').append('<li>' + response.tag_names[j] + '</li>');
                            }
                        }
                    }
                    $('#add-tags-modal').modal('hide');

                } else {
                    if(response.error == 'missing-parameter') {
                        $('#add-tags-modal .modal-header').after('<div class="modal-message">'+gettext('Incomplete information to add tags')+'</div>');
                    } else if(response.error == 'invalid-publication') {
                        $('#add-tags-modal .modal-header').after('<div class="modal-message">'+gettext('File to add tags not found')+'</div>');
                    }

                }
            }, 'json');
        }

        return false;
    });

    // Delete Files Modal ----------------------------------------------------------------------------------------------

    $('#delete-files-confirmation-modal').on('show', function() {
        if(!$('.documents_table input[type="checkbox"]:checked').length) {
            return false;
        }

        $('#delete-files-confirmation-modal .modal-footer span').text($('.documents_table input[type="checkbox"]:checked').length);
    });

    $('#delete-files-confirmation-modal .modal-footer button.btn-danger').on('click', function(e) {
        var publications = new Array();

        $('.documents_table input[type="checkbox"]:checked').each(function(e) {
            publications.push($(this).closest('tr').attr('id'));
        });

        $.post('/ajax/' + var_organization_slug + '/publication/delete/', {uid:publications, shelf:shelf_id}, function(response) {
            $('#delete-files-confirmation-modal').modal('hide');

            if(response.status == 'success') {
                $('.documents_table input[type="checkbox"]:checked').each(function(e) {
                    $(this).closest('tr').remove();
                });

                $('.checkbox_actions input[type="checkbox"]').attr('checked', false);
                $('.checkbox_actions').removeClass('checkbox_actions_selected').find('a').addClass('disabled');

            } else {
                if(response.error == 'invalid-publication') {
                    $('#message_modal').modal('show').find('.modal-body p').text(gettext('File not found'));
                }
            }
        }, 'json');
        return false;
    });

    // PUBLICATION MODAL -----------------------------------------------------------------------------------------------

    $('#publication-modal').on('publication_updated', function(e, uid, title, tags) {
        $('#' + uid + ' .js-open-publication').attr('title', title).text(title);

        if(tags) {
            var tagnames = tags.split(',');
            var tag_html = '';
            for(var i=0; i<tagnames.length; i++) {
                tag_html = tag_html + '<li>' + tagnames[i] + '</li>'
            }
            $('#' + uid + ' .tag ul').html(tag_html);
        } else {
            $('#' + uid + ' .tag ul').remove();
        }
    });

    $('#publication-modal').on('publication_replaced', function(e, uid, file_ext, file_size) {
        $('#' + uid + ' .download a').attr('title', gettext('Download file')+' ' + file_ext.toUpperCase()).attr('data-content', gettext('File size')+' ' + file_size);
    });

    $('#publication-modal').on('publication_deleted', function(e, uid) {
        $('#' + uid).remove();

        if(!$('.documents_table tr').length) {
            $('.documents-content').html('<div class="no_publication">'+ gettext('File not found') +'</div>');
        }
    });
}