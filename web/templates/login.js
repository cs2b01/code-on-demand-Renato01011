$('.message a').click(function(){
   $('form').animate({height: "toggle", opacity: "toggle"}, "slow");
});

function getData(){
        $('#action').html("Authenticating...");
        $('#loading').show()
        var username = $('#username').val();
        var password = $('#password').val();
        var message = JSON.stringify({
                "username": username,
                "password": password
            });

        $.ajax({
            url:'/authenticate',
            type:'POST',
            contentType: 'application/json',
            data : message,
            dataType:'json',
            success: function(response){
                //alert(JSON.stringify(response));
                $('#action').html(response['statusText']);
                $('#loading').hide()
                $('#ok').show()
            },
            error: function(response){
                //alert(JSON.stringify(response));
                $('#action').html(response['statusText']);
                $('#loading').hide()
                $('#notok').show()
            }
        });
    }

