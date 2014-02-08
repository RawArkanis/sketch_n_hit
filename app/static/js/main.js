'use strict';

var error_tmpl = _.template(
    '<div class="alert alert-danger" id="danger">\n' +
    '  <strong><%= title %></strong> <%= message %>\n' +
    '</div>\n'
);

$(document).ready(function() {
  $.ajaxSetup({ cache: true });
  $.getScript('//connect.facebook.net/en_UK/all.js', function() {
    FB.init({
        appId: '595127900566216',
        status: true,
        cookie: true,
        oauth: true
    });

    //FB.getLoginStatus();

    if ($('#board') !== undefined)
        var defaultBoard = new DrawingBoard.Board('board',{ webStorage: false });
  });
});

function createError(data) {
    $('#danger').remove();
    $('#container').prepend(error_tmpl(data));

    $('html, body').animate({ scrollTop: 0 }, 'slow');
}

function inviteFriends() {
    FB.ui({method: 'apprequests',
      message: 'Come play Sketch\'n\'Hit with me!'
    }, function() {

    });
}

function selectFriend(id) {
    $('#friend_id').val(id);

    var name = $('#friend_name_' + id).html();

    $('#friend_input').val(name);
}

function validadeCreateDraw() {
    var user_id = $('#user_id').val();
    var friend_id = $('#friend_id').val();
    var drawing_id = $('input[name=drawing_id]:checked').val();
    var data = $('.board canvas').get(0).toDataURL();

    if (user_id == '' || friend_id == '' || drawing_id == undefined) {
        createError({
            'title': 'Wait!',
            'message': 'You need to fill all the fields before sending. '
        });

        return false;
    }

    $('#data').val(data);

    return true;
}
