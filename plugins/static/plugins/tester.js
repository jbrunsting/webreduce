var HANDLER_TIMEOUT = 10000;

function testCode(code, showModal, onResult, onError, config, paginationData) {
    var timedOut = false;
    var completed = false;

    function configured() {
        return typeof getConfigModal === 'undefined' ||
            (typeof validateConfig === 'undefined' && !!config) ||
            (typeof validateConfig !== 'undefined' && validateConfig(config));
    }

    function onResultOrTimeout(result) {
        if (timedOut || completed) {
            return;
        }
        completed = true;
        onResult(result);
    }

    function fetchPostsWithTimeout() {
        if (!configured()) {
            onError("The plugin config is not valid");
            return;
        }

        try {
            fetchPosts(onResultOrTimeout, config, paginationData);
            setTimeout(function() {
                if (!completed) {
                    timedOut = true;
                    onError("Timed out waiting for fetchPosts callback");
                }
            }, HANDLER_TIMEOUT);
        } catch (e) {
            completed = true;
            onError(e);
        }
    }

    try {
        eval(code);

        if (!fetchPosts) {
            throw "function 'fetchPosts' not defined";
        }

        if (configured()) {
            fetchPostsWithTimeout();
        } else {
            showModal(getConfigModal(function(newConfig) {
                hideModal();
                config = newConfig;
                fetchPostsWithTimeout();
            }, config), function() {
                onError("The plugin configuration was canceled");
            });
        }
    } catch (e) {
        onError(e);
        return;
    }
}
