bkLib.onDomLoaded(function() {
    var questionNicEditor = new nicEditor({
        uploadURI: "/image_upload/",
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
    var tag_list = "";

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
    $question_tag = $(".tag");
    $question_tag_editable = $(".tag-editable");
    $question_tag_edit = $("#tag-edit");
    $question_tag_edit_input = $('#tag-edit input');

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


        $question_tag.hide();
        $question_tag_edit.show();

        tag_list = $($question_tag).text();
        tag_list = tag_list.replace(/\s\s+/g, ' '); // remove extra spaces
        tag_list = tag_list.trim();                 // trim spaces
        var tag_array = tag_list.split(" ");        // split the list of tags into seperate tags

        tag_list = "";
        // Load all previous tags to input field
        for(var i=0;i<tag_array.length;i++)
        {
            $question_tag_edit_input.val(tag_array[i]);
            $question_tag_edit_input.focusout();
        }

    }
/* Tag input */
$(function(){

// Handle conversion of tags into buttons
  $question_tag_edit_input.on({
    focusout : function() {
      var txt = this.value.replace(/[^a-z0-9\+\-\.\#]/ig,''); // allowed characters
      if(txt) $("<span/>", {text:txt.toLowerCase(), insertBefore:this});
      tag_list = this.value.trim()+" "+tag_list;

      this.value = "";
    },

    //Handles event when space is fired
    keyup : function(ev) {
      $('.tag_button').show();
      if(/(32)/.test(ev.which))
        var written_tags = tag_list;
        if(written_tags.search(this.value)==-1)
          $(this).focusout();
        else
          this.value = "";
    }
    });
  // Handles event for deleting tags when cancel button is clicked
  $question_tag_edit.on('click', 'span', function() {

    var tag_text = tag_list;
    var span_text = $(this).text();
    tag_text = tag_text.replace(span_text+" ","");

    tag_list = tag_text;
    $(this).remove();
    });

});
    $question_title_editable.click(function(){
        modify($question_edit);
    });
    $question_edit.click(function () {
        modify($question_edit);
    });

   $question_save.click(function () {
        $saving.show();
        $(this).hide();
        $question_title.text($question_title_edit_input.val());
        tag_list = tag_list.trim()
        var tag_array = tag_list.split(" ");
        $question_tag.html('');
        for(var i=0;i<tag_array.length;i++){
            $question_tag.html($question_tag.html()+"<span class='category'>\
                                <a href='/filter_tags/"+tag_array[i]+"/' >"+tag_array[i]+"</a></span>");
        }
        $question_title_edit.hide();
        $question_title.show();
        $question_tag_edit.hide();
        $question_tag.show();
        $questionNicPanel.hide();
        $question_details_edit.hide();
        $(this).prev().css("display", "block");
        
        /* make the ajax call */
        //var id_length = $question_save.attr("id").length;
        //var question_id = parseInt($question_save.attr("id").substr(id_length-1));
        var question_id = parseInt($question_save.data("qid"));
        var question_title = $question_title.text();
        var question_body = $questionInstance.html();
        var question_tag = tag_list;

        tag_list = "";
        $("#Tags").find("span").remove();
        $.ajax({
            url: "/ajax-question-update/",
            data:{
                question_id: question_id,
                question_title: question_title,
                question_body: question_body,
                question_tag: question_tag,
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
        uploadURI: "/image_upload/",
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
       uploadURI: "/image_upload/",
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
            uploadURI: "/image_upload/",
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
        var answer_id = $(this).data("aid");
        var form = $(this).data("form");
        $form = $("#"+form);
        nics[target].instanceById(target).saveContent();
        var text = (nics[target].instanceById(target).getContent());
        text = text.replace(/<br ?\/?>/g, "\n")
        text = text.replace(/&nbsp;/g, ' ');
        if(text.trim().length > 0 ){
            $form.submit();
            e.preventDefault;
        }
         else{
            alert("Kindly write a comment")
            return false;
        }
    });
});
