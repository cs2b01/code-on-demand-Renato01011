$('.message a').click(function(){
   $('form').animate({height: "toggle", opacity: "toggle"}, "slow");
});

function getData() {
        $('#notok').hide();
        $('#ok').hide();
        $('#Chat').hide();
        var username = $('#username').val();
        var password = $('#password').val();
        var message = JSON.stringify({"username": username, "password": password});

        $.ajax({
            url:'/authenticate',
            type: 'POST',
            contentType: 'application/json',
            data: message,
            datatype: 'json',
            error: function(response) {
                if (response['status'] == 200) {
                    $('#action').html(response['statusText']);
                    $('#ok').show();
                    $('#Chat').show();
                }
                else {
                    $('#action').html(response['statusText']);
                    $('#notok').show();
                }
            },
            success: function(response) {
                //alert(JSON.stringify(response));
                $('#action').html(response['statusText']);
                $('#notok').show();
            }
        });
    }
