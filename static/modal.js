var MODAL_HTML = "" +
    "<div id=\"modal\">" +
    "  <div id=\"modal-content\">" +
    "  </div>" +
    "</div>";

$("body").append(MODAL_HTML);

function showModal(contents, onCancel) {
    var modalContent = $("#modal-content");
    var modal = $("#modal");

    modalContent.empty();
    modalContent.append(contents);

    modal.css("display", "flex");
    modal.click(function() {
      modal.hide();
      if (onCancel) {
          onCancel();
      }
    });

    modalContent.click(function(event) {
        event.stopPropagation();
    });
}

function hideModal() {
    $("#modal").hide();
}
