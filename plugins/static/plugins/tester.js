function testCode(code, setModal, onResult, onError, config, paginationData) {
    try {
        testCodeUnsafe(code, setModal, onResult, onError, config, paginationData);
    } catch(e) {
        onError(e);
        return;
    }
}

function testCodeUnsafe(code, setModal, onResult, onError, config, paginationData) {
    eval(code);

    if (!fetchPosts) {
        throw "function 'fetchPosts' not defined";
    }

    if (getConfigModal && (!config || (validateConfig && !validateConfig(config)))) {
        setModal(getConfigModal(config, function(newConfig) {
            config = newConfig;
            onResult(fetchPosts(config, paginationData));
            setModal("");
        }));
    } else {
        onResult(fetchPosts(config, paginationData));
    }
}
