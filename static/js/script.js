// close success / error messages automatically after 3 seconds
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert.auto-hide').forEach(function (el) {
        setTimeout(function () {
            bootstrap.Alert.getOrCreateInstance(el).close();
        }, 3000);
    });
});
