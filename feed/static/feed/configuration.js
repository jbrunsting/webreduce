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

function configure(subscription, showModal, csrfToken, onConfig, onCancel) {
    if (!subscription.getConfigModal) {
        return;
    }

    var modal = subscription.getConfigModal(function(config) {
        hideModal();
        saveConfig(subscription.id, config, csrfToken);
        onConfig(config);
    }, subscription.config);
    showModal(modal, onCancel);
}
