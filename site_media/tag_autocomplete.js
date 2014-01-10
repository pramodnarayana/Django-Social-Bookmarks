$(document).ready(function () {
    function split( val ) {
        return val.split(' ');
    }
    function extractLast( term ) {
        return split( term ).pop();
    }
    var csrftoken = $('input[name= csrfmiddlewaretoken]').val()
    $("#id_tags").autocomplete({
        minLength : 1,
        source : function(request, response) {
                     $.post(
                         '/ajax/tag/autocomplete', 
                         {
                             csrfmiddlewaretoken: csrftoken, 
                             term : extractLast(request.term)
                         },
                         function(result) { 
                             response(result);
                         },
                         'json'
                     );
                 },
        multiple : true, 
        focus : function() {
                    // prevent value inserted on focus
                    return false;
                },
        select : function( event, ui ) {
            var terms = split(this.value);
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push(ui.item.value);
            // add placeholder to get the comma-and-space at the end
            terms.push(" ");
            this.value = terms.join(" ");
            return false;
        }    
        });
});

