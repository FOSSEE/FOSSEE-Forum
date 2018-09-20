$(document).ready(function() {
    $category = $("#id_category");
    $tutorial = $("#id_tutorial");
    var tutorial = $tutorial.val();
    var category = $category.val();
    $tutorial.hide();
    function reset() {
        console.log('resetting')
        for (var i = 0, l = arguments.length; i < l; i ++) {
            switch(arguments[i]) {
                case "tutorial":
                    $tutorial.html("<option value='None'>Select a Sub Category</option>");
                    break;
            }
        }
    }

    $category.change(function() {
        $("#similar-link").hide();
        /* resetting dropdowns */
        reset("tutorial");
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
