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

function getModal(subscription, onConfig) {
    var container = $("<div></div>");
    if (subscription.getConfigModal) {
        container.append(subscription.getConfigModal(onConfig, subscription.config));
    }
    return container.get();
}

function configure(subscription, showModal, csrfToken, onConfig, onCancel) {
    var modal = getModal(subscription, function(config) {
        hideModal();
        saveConfig(subscription.id, config, csrfToken);
        onConfig(config);
    });
    showModal(modal, onCancel);
}
