$(document).ready(function(){
    $('#search-form').submit(function(){
        var query = $('#id_query').val();
        $('#search-result').load(
            '/search/?ajax&query=' + encodeURIComponent(query)
        );
        return false
    });
})
