bkLib.onDomLoaded(function() {
    var questionNicEditor = new nicEditor({
        fullPanel : true,
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image', 'link', 'forecolor', 'bgcolor'],
        iconsPath: "/static/website/js/nicEditorIcons.gif",
    });
    questionNicEditor.setPanel('questionNicPanel');
    questionNicEditor.addInstance('questionInstance');
});

$(document).ready(function() {
    /*
     * question edit section
     * set the jquery variables 
    */
    $saving = $(".saving");
    $saved= $(".saved");
    $question = $(".question");
    $question_modify = $(".question .modify");
    $question_edit = $(".question .modify .edit");
    $question_save = $(".question .modify .save");
    $question_title = $(".title");
    $question_title_editable = $(".title-editable");
    $question_title_edit = $("#title-edit");
    $question_title_edit_input = $("#title-edit input");
    $questionNicPanel = $("#questionNicPanel");
    $questionInstance = $("#questionInstance");
    $question_details_edit = $("#question-details-edit");

    /* make the question editable and show modify */
    //$question.addClass("editable");
    $question_modify.show();

    /* edit and save click events */
    function modify(thisObj){
        thisObj.hide();
        thisObj.next().css("display", "block");
        
        $question_title.hide();
        $question_title_edit_input.val($.trim($($question_title).text()));
        $question_title_edit.show();
        $question_edit.hide();
        $question_save.show();
        
        $questionNicPanel.show();
        $questionInstance.focus();
        $question_details_edit.show();
    }
    $question_title_editable.click(function(){
        modify($question_edit);
    });
    $question_edit.click(function () {
        modify($question_edit);
    });
    $questionInstance.click(function() {
        modify($question_edit);
    });
    $question_save.click(function () {
        $saving.show();
        $(this).hide();
        $question_title.text($question_title_edit_input.val());
        $question_title_edit.hide();
        $question_title.show();
        $questionNicPanel.hide();
        $question_details_edit.hide();
        $(this).prev().css("display", "block");
        
        /* make the ajax call */
        //var id_length = $question_save.attr("id").length;
        //var question_id = parseInt($question_save.attr("id").substr(id_length-1));
        var question_id = parseInt($question_save.data("qid"));
        var question_title = $question_title.text();
        var question_body = $questionInstance.html();
        $.ajax({
            url: "/ajax-question-update/",
            data:{
                question_id: question_id,
                question_title: question_title,
                question_body: question_body,
            },
            type: "POST",
            dataType: "html",
            success: function(data){
                $saving.hide();
                $saved.show();
                $saved.fadeOut("slow");
            }
        });
    });
    
    /*
     * question details edit section
     * handle everything in the popup
    */
    $question_details_edit = $("#question-details-edit");
    $question_details_ok = $("#question-details-ok");
    $question_category = $('#id_category');
    $question_tutorial = $('#id_tutorial');
    $question_minute_range = $('#id_minute_range');
    $question_second_range = $('#id_second_range');
    
    $question_details_ok.click(function() {
        $saving.show();
        var category = $question_category.val();
        var tutorial = $question_tutorial.val();
        var minute_range = $question_minute_range.val();
        var second_range = $question_second_range.val();
        
        $.ajax({
            url: "/ajax-details-update/",
            data: {
                qid: $(this).data("qid"),
                category: category,
                tutorial: tutorial,
                minute_range: minute_range,
                second_range: second_range
            },
            type: "POST",
            success: function(data){
                if(category != 'None') {
                    $(".category small a").html(category);
                    $(".category").show()
                } else {
                    $(".category").hide()
                }
                if(tutorial!= 'None') {
                    $(".tutorial small a").html(tutorial);
                    $(".tutorial").show()
                } else {
                    $(".tutorial").hide()
                }
                if(minute_range!= 'None') {
                    $(".minute_range small a").html(minute_range);
                    $(".minute_range").show()
                } else {
                    $(".minute_range").hide()
                }
                if(second_range != 'None') {
                    $(".second_range small a").html(second_range);
                    $(".second_range").show()
                } else {
                    $(".second_range").hide()
                }
                $saving.hide();
                $saved.show();
                $saved.fadeOut("slow");
            }
        });
    });

    /*
     * answer edit section
     * set the dom variables
    */
    $answer_edit = $('.answer .edit');
    $answer_save = $(".answer .save");
    $answerPanelWrapper = $("#answerPanelWrapper");

    var answerNicEditor = new nicEditor({
        fullPanel : true,
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image', 'link', 'forecolor', 'bgcolor'],
        iconsPath: "/static/website/js/nicEditorIcons.gif",
    });
    answerNicEditor.panelInstance('answerNicPanel');

    $answer_edit.click(function(e) {
        var target = $(this).data("target");
        answerNicEditor.addInstance(target);
        $(this).parents("div.answer").prepend($answerPanelWrapper);
        $answerPanelWrapper.show();
        $('#answerPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $('#answerPanelWrapper .nicEdit-panelContain').parent().next().width('100%');
        $(this).hide();
        $(this).next().show();
        $("#"+target).focus();
        e.preventDefault();
    });

    $answer_save.click(function() {
        $saving.show();
        var target = $(this).data("target");
        answerNicEditor.removeInstance(target);
        $answerPanelWrapper.hide();
        $('#answerPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $(this).hide();
        $(this).prev().show();
        
        var answer_id = parseInt($(this).data("aid"));
        var answer_body = $("#"+target).html();
        
        $.ajax({
            url: "/ajax-answer-update/",
            type: "POST",
            data: {
                answer_id: answer_id,
                answer_body: answer_body
            },
            success: function(data) {
                $saving.hide();
                $saved.show();
                $saved.fadeOut("slow");
            }
        });
    });

    /*
     * comment edit section
     * set the dom variables
     */
    $comment = $(".comment");
    $comment_edit = $(".comment .edit");
    $comment_save = $(".comment .save");
    $commentPanelWrapper = $("#commentPanelWrapper");

    $comment.mouseover(function(){
        $(this).find(".modify-wrapper").show();
    });
    $comment.mouseout(function(){
        $(this).find(".modify-wrapper").hide();
    });
    var commentNicEditor = new nicEditor({
        fullPanel : true,
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image', 'link', 'forecolor', 'bgcolor'],
        iconsPath: "/static/website/js/nicEditorIcons.gif",
    });
    commentNicEditor.panelInstance('commentNicPanel');
    
    $comment_edit.click(function(e) {
        var target = $(this).data("target");
        
        commentNicEditor.addInstance(target);
        $(this).parents("div.comment").prepend($commentPanelWrapper);
        $commentPanelWrapper.show();
        $('#commentPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $('#commentPanelWrapper .nicEdit-panelContain').parent().next().width('100%');
        $(this).hide();
        $(this).next().show();
        $("#"+target).focus();
        e.preventDefault();
    });

    $comment_save.click(function() {
        $saving.show();
        var target = $(this).data("target");
        commentNicEditor.removeInstance(target);
        $commentPanelWrapper.hide();
        $('#commentPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $(this).hide();
        $(this).prev().show();
        
        var comment_id = parseInt($(this).data("cid"));
        var comment_body = $("#"+target).html();
        $.ajax({
            url: "/ajax-answer-comment-update/",
            type: "POST",
            data: {
                comment_id: comment_id,
                comment_body: comment_body
            },
            success: function(data) {
                $saving.hide();
                $saved.show();
                $saved.fadeOut("slow");
            }
        });
    });
    
    /*
     * add a new comment
     * set the dom variables
    */
    var nics = {};
    $add_comment = $(".add-comment");
    $cancel_commment = $(".cancel-comment");
    $post_comment = $(".post-comment");
    $add_comment.click(function(e) {
        $(this).hide();
        $(this).siblings(".cancel-comment").show();
        $(this).siblings(".post-comment").show();
        
        var target = $(this).data("target");
        $("#"+target).show();
        
        nics[target] = new nicEditor({
            fullPanel : true,
            buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image', 'link'],
            iconsPath: "/static/website/js/nicEditorIcons.gif",
        }).panelInstance(target, {hasPanel : true});
        e.preventDefault();
    });

    $cancel_commment.click(function(e) {
        $(this).hide();
        $(this).siblings(".post-comment").hide();
        $(this).siblings(".add-comment").show();
        
        var target = $(this).data("target");
        
        nics[target].removeInstance(target);
        nics[target] = null;
        $("#"+target).hide();
        e.preventDefault();
    });

    $post_comment.click(function(e) {
        var target = $(this).data("target");
       // alert(target);
        var answer_id = $(this).data("aid");
        var form = $(this).data("form");
        $form = $("#"+form);
        nics[target].instanceById(target).saveContent();
        var text = (nics[target].instanceById(target).getContent());
        // alert(text)
        text = text.replace(/<br ?\/?>/g, "\n")
        text = text.replace(/&nbsp;/g, ' ');
        // alert(text+"after");
        // alert(text.trim().length);
        if(text.trim().length > 0 ){
            $form.submit();
            e.preventDefault;
        }
         else{
            alert("Kindly write a comment")
            return false;
        }
    });

     $('.delete-question').on('click', function(e){
        question_id = parseInt($('.delete-question').data("qid"));
        $('#confirm-delete').modal({ backdrop: 'static', keyboard: false })
        .one('click', '#delete', function() {
            $.ajax({
                url: "/ajax-delete-question/",
                type: "POST",
                data: {
                    question_id: question_id,
                },
                success: function(data) {
                    $deleted.hide();
                    $deleted.show();
                    $deleted.fadeOut(10000);
                    window.location = '/';
                }
            });
        });
    });

    /* hide */
    $('.hide-question').on('click', function(e){
        question_id = parseInt($('.hide-question').data("qid"));
        status = parseInt($('.hide-question').data("status"));
        $('#confirm-hide').modal({ backdrop: 'static', keyboard: false })
        .one('click', '#chide', function() {
            $.ajax({
                url: "/ajax-hide-question/",
                type: "POST",
                data: {
                    question_id: question_id,
                    status : status,
                },
                success: function(data) {
                    $hide_qmsg.hide();
                    $hide_qmsg.show();
                    $hide_qmsg.fadeOut(10000);
                    window.location.reload();
                }
            });
        });
    });
});

});
