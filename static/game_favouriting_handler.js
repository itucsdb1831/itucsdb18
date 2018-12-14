document.addEventListener("DOMContentLoaded", function(is_game_favourite) {
    var dom_element = document.getElementById("div_favourite")

    if(is_game_favourite == true) {
        dom_element[0].innerHtml = "*FAVOURITE*";
        dom_element[1].style.display = "block";
        dom_element[2].style.display = "none";
    }
    else {
        dom_element[0].innerHtml = "";
        dom_element[1].style.display = "none";
        dom_element[2].style.display = "block";
    }
});

function addToFavourites(user_id, game_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_game_favouriting');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById(user_id_to).innerHtml = data.responseText;
        document.getElementById("column_favourite").innerHtml = data.column_favourite;
    }

    const data = new FormData();
    data.append('operation', 'ADD');
    data.append('user_id', user_id);
    data.append('game_id', game_id);

    request.send(data);
}

function removeFromFavourites(user_id, game_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_game_favouriting');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById(user_id_to).innerHtml = data.responseText;
        document.getElementById("column_favourite").innerHtml = data.column_favourite;
    }

    const data = new FormData();
    data.append('operation', 'REMOVE');
    data.append('user_id', user_id);
    data.append('game_id', game_id);

    request.send(data);
}
