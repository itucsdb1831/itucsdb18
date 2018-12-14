function playGame(user_id, game_id, time_played) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_play_game');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById("column_time_played").innerHtml = data.time_played + " hours";
    }

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('game_id', game_id);
    data.append('time_played', time_played);

    request.send(data);
}