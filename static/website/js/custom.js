$(document).ready(function() {
    $category = $("#id_category");
    $tutorial = $("#id_tutorial");
    $minute_range = $("#id_minute_range");
    $second_range = $("#id_second_range");

    $category.change(function() {
        $("#similar-link").hide();
        var category = $(this).val();
        /* see thread-user.js */
        $("#question-details-ok").show();
        $.ajax({
            url: "/ajax-tutorials/",
            type: "POST",
            data: {
                category: category
            },
            success: function(data) {
                $("#id_tutorial").html(data);
                $("#id_tutorial").removeAttr("disabled");
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
    
    $second_range.change(function() {
        $.ajax({
            url: "/ajax-similar-questions/",
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
                $response = $(data);
                var similar_count= $response.find("#similar-count").text();
                $("#similar-link").show().html(similar_count);
                $("#modal-body").html(data);
            }
        });
    });


    $(document).ajaxStart(function() {
        $("#ajax-loader").show();
    });

    $(document).ajaxStop(function() {
        $("#ajax-loader").hide();
    });
});
