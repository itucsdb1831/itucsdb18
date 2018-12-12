document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('.timeobj').forEach(function(x) {
        var d = new Date();
        d.setTime(parseInt(x.innerHTML) - d.getTimezoneOffset() * 60 * 1000);

        x.innerHTML = d.toLocaleDateString() + " " + d.toLocaleTimeString().substr(0, 5);
    });
});
