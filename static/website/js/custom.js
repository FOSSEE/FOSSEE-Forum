$(document).ready(function() {
 $("#id_category").val($category); 

    $tutorial = $("#id_tutorial");
    $minute_range = $("#id_minute_range");
    $second_range = $("#id_second_range");

/*    function reset() {
        for (var i = 0, l = arguments.length; i < l; i ++) {
            switch(arguments[i]) {
                case "tutorial":
                    $tutorial.html("<option value='None'>Select a Tutorial</option>");
                    $tutorial.attr("disabled", true);
                    break;
                
                case "minute_range":
                    $minute_range.html("<option value='None'>min</option>");
                    $minute_range.attr("disabled", true);
                    break;
                
                case "second_range":
                    $second_range.html("<option value='None'>sec</option>");
                    $second_range.attr("disabled", true);
                    break;
                
            }
        }
    }
    $category.change(function() {
        $("#similar-link").hide();
        reset("tutorial", "minute_range", "second_range");
        $("#question-details-ok").show();
        var category = $(this).val();
        if(category == "General") {
            $tutorial.html("<option value='None'>Not required</option>");
            $tutorial.removeAttr("disabled");
            $minute_range.html("<option value='None'>Not required</option>");
            $minute_range.removeAttr("disabled");
            $second_range.html("<option value='None'>Not required</option>");
            $second_range.removeAttr("disabled");
        } else {
            $.ajax({
                url: "/ajax-tutorials/",
                type: "POST",
                data: {
                    category: category
                },
                success: function(data) {
                    $("#id_tutorial").html(data);
                    $("#id_tutorial").removeAttr("disabled");
                }
            });
        }
    });
*/
    $tutorial.change(function() {
        /* resetting dropdowns */
        reset("minute_range", "second_range");

        var tutorial = $(this).val();
        if(tutorial == "General") {
            /* disabling all other fields */
            $minute_range.html("<option value='None'>Not required</option>");
            $minute_range.removeAttr("disabled");
            $second_range.html("<option value='None'>Not required</option>");
            $second_range.removeAttr("disabled");
        } else {
            $.ajax({
                url: "/ajax-duration/",
                type: "POST",
                data: {
                    category: category,
                tutorial: tutorial
                },
                success: function(data){
                    var $response = $(data);
                    $minute_range.html($response.find("#minutes").html())
                    $minute_range.removeAttr("disabled");
                    $second_range.html($response.find("#seconds").html())
                    $second_range.removeAttr("disabled");
                }
            });
        }
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
