$(function() {
    $('select').select(function() {
        var table = $('#table').val();
        $.ajax({
            url: '/table',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});