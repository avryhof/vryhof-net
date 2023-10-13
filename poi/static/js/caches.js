document.onload = function () {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function (location) {
            $('#id_latitude').val(location.coords.latitude);
            $('#id_longitude').val(location.coords.longitude);
        });
    }
}