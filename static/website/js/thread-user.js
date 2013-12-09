bkLib.onDomLoaded(function() {

    var questionNicEditor = new nicEditor({
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image'],
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
    $question = $(".question");
    $question_modify = $(".question .modify");
    $question_edit = $(".question .modify .edit");
    $question_save = $(".question .modify .save");
    $questionNicPanel = $("#questionNicPanel");
    $questionInstance = $("#questionInstance");

    /* make the question editable and show modify */
    $question.addClass("editable");
    $question_modify.show();

    /* edit and save click events */
    function modify(thisObj){
        thisObj.hide();
        thisObj.next().css("display", "block");
        $questionNicPanel.show();
        $questionInstance.focus();
    }
    $question_edit.click(function () {
        modify($question_edit);
    });
    $questionInstance.click(function() {
        modify($question_edit);
    });
    $question_save.click(function () {
        $(this).hide();
        $questionNicPanel.hide();
        $(this).prev().css("display", "block");

        /* make the ajax call */
        var id_length = $question_save.attr("id").length;
        var question_id = parseInt($question_save.attr("id").substr(id_length-1));
        console.log(question_id);
        var question_body = $questionInstance.html();
        $.ajax({
            url: "/ajax-question-update/",
            data:{
                question_id: question_id,
                question_body: question_body,
            },
            type: "POST",
            dataType: "html",
            success: function(data){
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
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image'],
        iconsPath: "/static/website/js/nicEditorIcons.gif",
    });
    replyNicEditor.panelInstance('replyNicPanel');

    $reply_edit.click(function() {
        var reply_body = $(this).data("target");
        console.log(reply_body);
        replyNicEditor.addInstance(reply_body);
        $(this).parents("div.reply").prepend($replyPanelWrapper);
        $replyPanelWrapper.show();
        $('#replyPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $('#replyPanelWrapper .nicEdit-panelContain').parent().next().width('100%');
        $(this).hide();
        $(this).next().show();
    });

    $reply_save.click(function() {
        var reply_body = $(this).data("target");
        replyNicEditor.removeInstance(reply_body);
        $replyPanelWrapper.hide();
        $('#replyPanelWrapper .nicEdit-panelContain').parent().width('100%');
        $(this).hide();
        $(this).prev().show();
    });
});

