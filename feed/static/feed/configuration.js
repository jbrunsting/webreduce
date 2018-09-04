function saveConfig(subscriptionId, config, csrfToken) {
    $.ajax({
        url: "/feed/configure/" + subscriptionId,
        type: "POST",
        data: JSON.stringify(config),
        headers: {
            "X-CSRFToken": csrfToken
        }
    });
}

function ConfigHandler(subscription, setModal, csrfToken) {
    var onSave;
    handler = {};

    function save(config) {
        saveConfig(subscription.id, config, csrfToken);
        setModal();
        if (onSave) {
            onSave();
        }
    }

    handler.showModal = function() {
        setModal(subscription.getConfigModal(save, subscription.config));
    }

    handler.configured = function() {
        return subscription.configValid;
    }

    handler.setConfigBtn = function(configBtn) {
        if (!subscription.getConfigModal) {
            configBtn.disabled = true;
        } else {
            configBtn.onclick = handler.showModal;
        }
    }

    handler.setOnSave = function(callback) {
        onSave = callback;
    }

    return handler;
}
