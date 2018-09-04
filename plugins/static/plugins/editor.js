function setupCodeBlocks() {
    codeEditors = {};
    $(".code").each(function(i, code) {
        var editor
        if ($(code).hasClass("readonly") || !$(code).is("textarea")) {
            editor = CodeMirror(function(elt) {
                code.parentNode.replaceChild(elt, code);
            }, {
                "value": code.innerHTML,
                "mode": "javascript",
                "lineNumbers": true,
                "lineWrapping": true,
                "readOnly": true
            });
        } else {
            editor = CodeMirror.fromTextArea(code, {
                "mode": "javascript",
                "lineNumbers": true,
                "lineWrapping": true
            });
        }
        codeEditors[code] = editor;
    });

    return codeEditors;
}
