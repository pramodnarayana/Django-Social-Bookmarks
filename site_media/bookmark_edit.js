function bookmark_save() {
    var item = $(this).parent();
    console_log(item)
    var data = {
        url: item.find('#id_url').val(),
        title: item.find('#id_title').val(),
        tags: item.find('#id_tags').val(),
        share: item.find('#id_share').val(),
        csrfmiddlewaretoken: $('input[name= csrfmiddlewaretoken]').val() 
    };
    $.post('/save/?ajax', data, function (result) {
        if (result != 'failure') {
            item.before($('li', result).get(0));
            item.remove();
            $('ul.bookmarks .edit').click(bookmark_edit);
        }
        else {
            alert('Failed to validate bookmark before saving.');
        }
    });
    return false;
}


function bookmark_edit() {
    var item = $(this).parent();
    console.log(item)
    var url = item.find('.title').attr('href')
    item.load('/save/?ajax&url=' + escape(url), null, function() {
        $('#save-form').submit(bookmark_save);
    });
    return false;
}

function bookmark_delete() {
	var item = $(this).parent();
	var data = {
		url: item.find('.title').attr('href'), 
		csrfmiddlewaretoken: $.cookie('csrftoken') // jquery cookie plugin is used to get token
	}
	$.post('/delete/?ajax', data, function (result) {
        if (result == 'Success') {
            item.remove();
        }
        else {
            alert('Bookmark deletion failed.');
        }
    });
    return false;
	
}

$(document).ready(function () {
    $("ul.bookmarks .edit").click(bookmark_edit);
    $("ul.bookmarks .delete_bookmark").click(bookmark_delete);
});

