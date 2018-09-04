var HANDLER_TIMEOUT = 15000;

function testCode(code, setModal, onResult, onError, config, paginationData) {
    var timedOut = false;
    var completed = false;

    function onResultOrTimeout(result) {
        completed = true;
        if (timedOut) {
            return;
        }
        onResult(result);
    }

    function fetchPostsWithTimeout() {
        fetchPosts(onResultOrTimeout, config, paginationData);

        setTimeout(function() {
            if (!completed) {
                timedOut = true;
                onError("Timed out waiting for fetchPosts callback");
            }
        }, HANDLER_TIMEOUT);
    }

    try {
        eval(code);

        if (!fetchPosts) {
            throw "function 'fetchPosts' not defined";
        }

        if (getConfigModal && (!config || (validateConfig && !validateConfig(config)))) {
            setModal(getConfigModal(function(newConfig) {
                setModal("");
                config = newConfig;
                fetchPostsWithTimeout();
            }, config));
        } else {
            fetchPostsWithTimeout();
        }
    } catch(e) {
        onError(e);
        return;
    }
}
