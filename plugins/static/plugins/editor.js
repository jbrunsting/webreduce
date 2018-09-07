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
                "readOnly": true,
                "scrollbarStyle": "null",
                "viewportMargin": Infinity
            });
        } else {
            editor = CodeMirror.fromTextArea(code, {
                "mode": "javascript",
                "lineNumbers": true,
                "lineWrapping": true,
                "scrollbarStyle": "null",
                "viewportMargin": Infinity
            });
        }
        codeEditors[code] = editor;
    });

    return codeEditors;
}
