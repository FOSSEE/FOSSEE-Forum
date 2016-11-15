$(document).ready(function() {
    $category = $("#id_category");
    $tutorial = $("#id_tutorial");
    $minute_range = $("#id_minute_range");
    $second_range = $("#id_second_range");
        var tutorial = $tutorial.val();
        var category = $category.val();
        $tutorial.hide();
        if (tutorial == "Select a Sub Category" || tutorial =="General"){
                        $minute_range.attr("disabled", true);
                        $second_range.attr("disabled", true);
        }else{
                        $minute_range.removeAttr("disabled");
                        $second_range.removeAttr("disabled");
        }
    function reset() {
        console.log('resetting')
        for (var i = 0, l = arguments.length; i < l; i ++) {
            switch(arguments[i]) {
                case "tutorial":
                    $tutorial.html("<option value='None'>Select a Sub Category</option>");
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
        /* resetting dropdowns */
        reset("tutorial", "minute_range", "second_range");
        /* see thread-user.js */
        $("#question-details-ok").show();
        var category = $(this).val();
        console.log(category);
        $tutorial.hide();
        if(category == "12"){
            console.log(category);
            $tutorial.show();
            $tutorial.removeAttr("disabled");
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

        // else {
        //     $.ajax({
        //         url: "/ajax-tutorials/",
        //         type: "POST",
        //         data: {
        //             category: category
        //         },
        //         success: function(data) {
        //             $("#id_tutorial").html(data);
        //             $("#id_tutorial").removeAttr("disabled");
        //         }
        //     });
        // }
    });

   
    $(document).ajaxStart(function() {
        $("#ajax-loader").show();
    });

    $(document).ajaxStop(function() {
        $("#ajax-loader").hide();
    });
});
