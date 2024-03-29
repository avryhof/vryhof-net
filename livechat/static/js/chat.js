var API_RESULT_KEY = "result";
var API_GENERIC_FAILURE = "bad";
var API_GENERIC_SUCCESS = "ok";

var chat_dialog_visible = false;
var session_continued = false;
var chat_started = false;
var message_div;

function get_messages(continue_chat) {
    $.ajax({
        url: "/livechat/get-messages/",
        method: 'GET',
        headers: {},
        data: {continue_chat: continue_chat},
        success: function (retn) {
            results = retn.result;

            for (var i in results) {
                message_div.append('<div class="chat-message ' + results[i].type + '">' +
                    '<strong>' + results[i].name + ':</strong> ' + results[i].message +
                    '</div>');
                message_div.stop().animate({
                    scrollTop: message_div[0].scrollHeight * 2
                }, 800);
            }
        },
        error: function (msg) {
            console.log("ERROR:");
            console.log(msg);
        }
    });
}

function send_message() {
    message = $("#chat-input").val();

    if (message) {
        $.ajax({
            url: "/livechat/send-message/",
            method: 'POST',
            headers: {},
            data: {message: message},
            success: function (retn) {
                $("#chat-input").val("");

                // if (!chat_started) {
                //     setInterval(get_messages, 3000);
                //     chat_started = true;
                // }

                get_messages()
            },
            error: function (msg) {
                console.log("ERROR:");
                console.log(msg);
            }
        });
    }
}

$(document).ready(function () {
    $("#chat-dialog").hide();
    message_div = $("#chat-messages");

    message_div.stop().animate({
        scrollTop: message_div[0].scrollHeight * 2
    }, 800);

    document.addEventListener("click", function (e) {
        if (e.target.className == "chat-answer") {
            e.preventDefault();
            $("#chat-input").val(e.target.innerText);
            send_message();
        }
    });

    $("#chat-notifier").click(function () {
        if (!chat_dialog_visible) {
            $("#chat-dialog").show("slow");
            chat_dialog_visible = true;
            if (!session_continued) {
                session_continued = true;
                get_messages(session_continued);
            }
        } else {
            $("#chat-dialog").hide("slow");
            chat_dialog_visible = false;
        }
    });

    $("#chat-send").click(function (e) {
        e.preventDefault();
        send_message();
    });

    $("#chat-input").keyup(function (e) {
        var code = e.key;
        if (code === "Enter") {
            e.preventDefault();
            send_message();
        }
    });

    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function (location) {
            $.ajax({
                url: "/livechat/set-location/",
                method: 'POST',
                headers: {},
                data: location.coords,
                success: function (retn) {
                    console.log("location set");
                },
                error: function (msg) {
                    console.log("ERROR:");
                    console.log(msg);
                }
            });
        });
    }
});
