$(document).ready(function() {
    /*
     * answer edit section
     * set the dom variables
    */
    $answer_edit = $('.answer .edit');
    $answer_save = $(".answer .save");

    $answer_edit.click(function(e) {
        var target = $(this).data("target");
        var id = $(this).attr("id");
        $("#"+id+"1").show();
        $("#"+id+"2").hide();
        $(this).hide();
        $(this).next().show();
    });

    $answer_save.click(function() {
        var id = $(this).attr('data-form');
        $("#"+id).submit();

    });

    /*
     * comment edit section
     * set the dom variables
     */

    $edit_comment = $(".edit-comment");
    $save_comment = $(".save-comment");
    $edit_comment.click(function(e){
        $(this).hide();
        var id = $(this).attr('data-id');
        $("#com"+id).show();
        $("#cbody"+id).hide();
        $("#editor"+id).show();
    });

    $save_comment.click(function(e){
        var id = $(this).attr('data-form');
        $("#save_comment"+id).submit()
    });

    /*
     * add a new comment
     * set the dom variables
    */
    $add_comment = $(".add-comment");
    $cancel_commment = $(".cancel-comment");
    $post_comment = $(".post-comment");
    $add_comment.click(function(e) {
        $(this).hide();
        var id = $(this).attr('id');
        $("#"+id+"1").show();
        $(this).siblings(".cancel-comment").show();
        $(this).siblings(".post-comment").show();
    });

    $cancel_commment.click(function(e) {
        $(this).hide();
        var id = $(this).siblings(".add-comment").attr('id');
        $(this).siblings(".post-comment").hide();
        $("#"+id+"1").hide();
        $(this).siblings(".add-comment").show();
    });

    $post_comment.click(function(e) {
        var id = $(this).attr('data-form');
        $("#"+id).submit();
    });
});
