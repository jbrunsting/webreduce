function saveConfig(config, csrfToken, modalContainer) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/feed/configure/" + subscription.id, true);
    xhttp.setRequestHeader("X-CSRFToken", csrfToken);
    xhttp.send(JSON.stringify(config));
}

function setupConfiguration(subscription, configBtn, setModal, csrfToken) {
    if (!subscription.getConfigModal) {
        configBtn.disabled = true;
        return;
    }

    function save(config) {
        saveConfig(config, csrfToken);
        setModal();
    }

    configBtn.onclick = function() {
        setModal(subscription.getConfigModal(subscription.config, save));
    }

    if (!subscription.configValid) {
        setModal(subscription.getConfigModal(subscription.config, save));
    }
}
