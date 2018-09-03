function setupCodeBlocks() {
    $(".code").each(function(i, code) {
        if ($(code).hasClass("readonly") || !$(code).is("textarea")) {
            CodeMirror(function(elt) {
                code.parentNode.replaceChild(elt, code);
            }, {
                "value": code.innerHTML,
                "mode": "javascript",
                "lineNumbers": true,
                "lineWrapping": true,
                "readOnly": true
            });
        } else {
            CodeMirror.fromTextArea(code, {
                "mode": "javascript",
                "lineNumbers": true,
                "lineWrapping": true
            });
        }
    });
}
