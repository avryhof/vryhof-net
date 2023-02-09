$(document).on("submit", "#search-form", function (e) {
    e.preventDefault();

    $.ajax({
        url: "/api/rest/search/",
        method: 'POST',
        headers: {},
        data: {q: $("#id_search").val()},
        success: function (retn) {
            $("#search-results").append('<div class="chat-bubble">' + retn.chat + '</div>');

            for (var i in retn.results) {
                var result_html = '<div class="title">' +
                    '<a href="' + retn.results[i].href + '">' + retn.results[i].title + '</a></div>' +
                    '<div class="body">' + retn.results[i].body + '</div>'

                $("#search-results").append('<div class="search-result">' + result_html + '</div>');
            }

        },
        error: function (msg) {
            console.log("ERROR:");
            console.log(msg);
        }
    });

});