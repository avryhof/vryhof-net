function confirmDialog(message, confirm_action, cancel_action) {
    var confirm_modal = $("#confirm-modal");
    if (confirm_modal.length === 0) {
        $("body").append(
            '<input type="checkbox" class="modal-control" id="confirm-modal-control">' +
            '<div id="confirm-modal" class="modal-container">' +
            '    <div class="modal-content">' +
            '        <div id="confirm-dialog" class="modal-dialog">' +
            '            <div class="modal-controls">' +
            '                <label for="confirm-modal-control" class="modal-close">' +
            '                    <i class="fa-solid fa-2x fa-circle-xmark"></i>' +
            '                    <span class="sr-only">Close</span>' +
            '                </label>' +
            '            </div>' +
            '            <div class="modal-row">' + message + '</div>' +
            '            <div class="modal-row">' +
            '                <a class="btn btn-primary" id="confirm-ok">Yes</a>' +
            '                <a class="btn btn-outline" id="confirm-cancel">No</a>' +
            '            </div>' +
            '        </div>' +
            '    </div>' +
            '</div>');
    }
    $("#confirm-modal-control").prop("checked", true);

    $(document).on("click", "#confirm-ok", function (e) {
        e.preventDefault();
        confirm_action();
        $("#confirm-modal-control").prop("checked", false);
    });

    $(document).on("click", "#confirm-cancel", function (e) {
        e.preventDefault();
        if (typeof (cancel_action) == "function") {
            cancel_action();
        }
        $("#confirm-modal-control").prop("checked", false);
    });
}