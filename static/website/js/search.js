$(document).ready(function() {
    $search_key = $("#search-key");
    $search_key_submit = $("#search-key-submit");
    $keyword_search_results = $("#keyword-search-results");

    $search_key.keyup(function(e) {
        if(e.keyCode == 13) {
            $search_key_submit.click();
        }
    });

    $search_key_submit.click(function() {
        var key = $search_key.val();
        $.ajax({
            url: "/ajax-keyword-search/",
            type: "POST",
            data: {
                key: key
            },
            dataType: "html",
            success: function(data) {
                $keyword_search_results.html(data);
                console.log(data);
            }
        });
    });
});
