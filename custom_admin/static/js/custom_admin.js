'use strict';
{

    jQuery.expr[":"].Contains = jQuery.expr.createPseudo(function (arg) {
        return function (elem) {
            return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
        };
    });
    $(document).ready(function () {
        $(".level-2.active").parents(".sidebar-item").children(".submenu-control").prop("checked", true);

        var query_field = $("#q");
        var filter_field = $(".filter-field");

        if (query_field.length > 0) {
            $(document).on("keyup", "#q", function (e) {
                e.preventDefault();
                // console.log($(this).val());
                if ($(this).val().length > 0) {
                    $(".left-nav ul li").hide();
                    $(".left-nav hr").hide();
                    $(".left-nav ul li:Contains(" + $(this).val() + ")").show();
                } else {
                    $(".left-nav ul li").show();
                    $(".left-nav hr").show();
                }
            });
        }

        if (filter_field.length > 0) {
            filter_field.each(function (e) {
                $(document).on("keyup", "#" + $(this).attr("id"), function (e) {
                    e.preventDefault();
                    var filter_element = $(this).data('element');
                    if ($(this).val().length > 0) {
                        $("#" + filter_element).children().hide();
                        $("#" + filter_element).children("*:Contains(" + $(this).val() + ")").show();
                    } else {
                        $("#" + filter_element).children().show();
                    }
                });
            });
        }

        $(document).on("keyup", "#searchbar", function (e) {
            e.preventDefault();
            if ($(this).val().length > 0) {
                $("#result_list tbody tr").hide();
                $("#result_list tbody tr:Contains(" + $(this).val() + ")").show();
            } else {
                $("#result_list tbody tr").show();
            }
        });
    });
}