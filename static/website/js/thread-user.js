bkLib.onDomLoaded(function() {
    var questionNicEditor = new nicEditor({
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image', 'link'],
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
                console.log(data);
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
        console.log($(this).data("qid"));
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
                console.log(data);
            }
        });
    });
    /*
     * reply edit section
     * set the dom variables
    */
    $reply_edit = $('.reply .edit');
    $reply_save = $(".reply .save");
    $replyPanelWrapper = $("#replyPanelWrapper");

    var replyNicEditor = new nicEditor({
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image', 'link'],
        iconsPath: "/static/website/js/nicEditorIcons.gif",
    });
    replyNicEditor.panelInstance('replyNicPanel');

    $reply_edit.click(function() {
        var target = $(this).data("target");
        console.log(target);
        replyNicEditor.addInstance(target);
        $(this).parents("div.reply").prepend($replyPanelWrapper);
        $replyPanelWrapper.show();
        $('#replyPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $('#replyPanelWrapper .nicEdit-panelContain').parent().next().width('100%');
        $(this).hide();
        $(this).next().show();
    });

    $reply_save.click(function() {
        $saving.show();
        var target = $(this).data("target");
        replyNicEditor.removeInstance(target);
        $replyPanelWrapper.hide();
        $('#replyPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $(this).hide();
        $(this).prev().show();
        
        var reply_id = parseInt($(this).data("rid"));
        var reply_body = $("#"+target).html();

        $.ajax({
            url: "/ajax-reply-update/",
            type: "POST",
            data: {
                reply_id: reply_id,
                reply_body: reply_body
            },
            success: function(data) {
                console.log(data);
                $saving.hide();
                $saved.show();
                $saved.fadeOut("slow");
            }
        });
    });
});

