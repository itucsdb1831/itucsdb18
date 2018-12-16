function addGameToFavourites(user_id, game_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_game_favouriting');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById("favourite_game_button").innerHtml = data.responseText;
        document.getElementById("is_game_favourite").innerHtml = data.column_favourite;
    }

    const data = new FormData();
    data.append('operation', 'ADD');
    data.append('user_id', user_id);
    data.append('game_id', game_id);

    request.send(data);
}

function removeGameFromFavourites(user_id, game_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_game_favouriting');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById("unfavourite_game_button").innerHtml = data.responseText;
        document.getElementById("is_game_favourite").innerHtml = data.column_favourite;
    }

    const data = new FormData();
    data.append('operation', 'REMOVE');
    data.append('user_id', user_id);
    data.append('game_id', game_id);

    request.send(data);
}
