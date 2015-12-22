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

    $search_time_submit = $("#search-time-submit");
    $category = $("#search-category");
    $tutorial = $("#search-tutorial");
    $minute_range = $("#search-minute-range");
    $second_range = $("#search-second-range");
    $time_search_results = $("#time-search-results");

    $category.change(function() {
        var category = $(this).val();
        $.ajax({
            url: "/ajax-tutorials/",
            type: "POST",
            data: {
                category: category
            },
            success: function(data) {
                $tutorial.html(data);
                $tutorial.removeAttr("disabled");
                console.log("response = " + data);
            }
        });
    });

    $tutorial.change(function() {
        console.log("tut changed");
        var category = $category.val();
        var tutorial = $(this).val();
        $.ajax({
            url: "/ajax-duration/",
            type: "POST",
            data: {
                category: category,
                tutorial: tutorial
            },
            success: function(data){
                var $response = $(data);
                console.log($response.html());
                $minute_range.html($response.find("#minutes").html())
                $minute_range.removeAttr("disabled");
                $second_range.html($response.find("#seconds").html())
                $second_range.removeAttr("disabled");
            }
        });
    });

    $search_time_submit.click(function() {
        $.ajax({
            url: "/ajax-time-search/",
            type: "POST",
            data: {
                category: $category.val(),
                tutorial: $tutorial.val(),
                minute_range: $minute_range.val(),
                second_range: $second_range.val()
            },
            dataType: "html",
            success: function(data) {
                console.log(data);
                $time_search_results.html(data);
            }
        });
    });
    
});
