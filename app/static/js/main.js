'use strict';

var word = '';
var letters = [];
var letters_no_repeat = [];
var hit = [];
var wrong = '';

var MAX_ERRORS = 5;
var errors = 0;

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

    if ($('#board').length > 0)
        var defaultBoard = new DrawingBoard.Board('board',{ webStorage: false });
    else if ($('#word').length > 0)
        initHit();
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

function initHit() {
    word = $('#word').val().toUpperCase();;
    letters = word.split('');

    for (var i = 0; i < letters.length; i++) {
        if (_.find(letters_no_repeat, function(chr) { return chr == letters[i] }) == undefined)
            letters_no_repeat.push(letters[i])
    }

    $('#word').remove();

    $(document).keypress(function(event){
        var ltr = String.fromCharCode(event.which).toUpperCase();

        var count = 0;

        for (var i = 1; i <= letters.length; i++) {
            if (letters[i-1] == ltr) {
                $('#letter_' + i).html(ltr);

                var ret = _.find(hit, function(chr) { return chr == ltr });
                if (ret == undefined)
                    hit.push(ltr);

                count++;
            }
        }

        if (count == 0) {
            errors++;
            wrong += ltr;
            $('#errors').html(wrong);
        }

        if (errors >= letters_no_repeat.length + MAX_ERRORS) {
            $(document).unbind('keypress');
            $('#place_m').html(word);
            $('#over_lose').modal({backdrop: 'static'})
        }
        if (hit.length == letters_no_repeat.length) {
            $(document).unbind('keypress');
            $('#place_h').html(word);
            $('#over_win').modal({backdrop: 'static'})
        }
     })
}
