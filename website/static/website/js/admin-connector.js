$(document).ready(function(){
    var editor = CodeMirror.fromTextArea(document.getElementById("id_template_body"), {
        lineNumbers: true,
        matchBrackets: true,
        mode: "application/x-ejs",
        indentUnit: 4,
        indentWithTabs: true,
        enterMode: "keep",
        tabMode: "shift"
    });
});