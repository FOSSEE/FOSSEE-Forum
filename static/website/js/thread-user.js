bkLib.onDomLoaded(function() {

    var questionNicEditor = new nicEditor({
        buttonList : ['fontSize','bold','italic','underline','strikeThrough','subscript','superscript','html','image'],
        iconsPath: "/static/website/js/nicEditorIcons.gif",
    });
    questionNicEditor.setPanel('questionNicPanel');
    questionNicEditor.addInstance('questionInstance');
});

$(document).ready(function() {
    /*set the jquery variables */
    $question = $(".question");
    $modify = $(".modify");
    $edit = $(".modify .edit");
    $save = $(".modify .save");
    $questionNicPanel = $("#questionNicPanel");
    $questionInstance = $("#questionInstance");

    /* make the question editable and show modify */
    $question.addClass("editable");
    $modify.show();

    /* edit and save click events */
    function modify(thisObj){
        thisObj.hide();
        thisObj.next().css("display", "block");
        $questionNicPanel.show();
        $questionInstance.focus();
    }
    $edit.click(function () {
        modify($edit);
    });
    $questionInstance.click(function() {
        modify($edit);
    });
    $save.click(function () {
        $(this).hide();
        $questionNicPanel.hide();
        $(this).prev().css("display", "block");

        /* make the ajax call */
        var id_length = $save.attr("id").length;
        var question_id = parseInt($save.attr("id").substr(id_length-1));
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
});

