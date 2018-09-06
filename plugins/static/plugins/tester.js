var HANDLER_TIMEOUT = 10000;

function testCode(code, setModal, onResult, onError, config, paginationData) {
    var timedOut = false;
    var completed = false;

    function onResultOrTimeout(result) {
        if (timedOut || completed) {
            return;
        }
        completed = true;
        onResult(result);
    }

    function fetchPostsWithTimeout() {
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

        if (typeof getConfigModal !== 'undefined' && (!config || (typeof validateConfig !== 'undefined' && !validateConfig(config)))) {
            setModal(getConfigModal(function(newConfig) {
                setModal("");
                config = newConfig;
                fetchPostsWithTimeout();
            }, config));
        } else {
            fetchPostsWithTimeout();
        }
    } catch (e) {
        onError(e);
        return;
    }
}
