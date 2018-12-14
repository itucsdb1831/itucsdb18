function cancelRequest(user_id_from, user_id_to) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_request_response');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById(user_id_to).innerHtml = data.fillerText;
    }

    const data = new FormData();
    data.append('response', 'cancelled');
    data.append('user_id_from', user_id_from);
    data.append('user_id_to', user_id_to);

    request.send(data);
}

function acceptRequest(user_id_from, user_id_to) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_request_response');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById(user_id_from).innerHtml = data.fillerText;
    }

    const data = new FormData();
    data.append('response', 'accepted');
    data.append('user_id_from', user_id_from);
    data.append('user_id_to', user_id_to);

    request.send(data);
}

function declineRequest(user_id_from, user_id_to) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_request_response');

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        document.getElementById(user_id_from).innerHtml = data.fillerText;
    }

    const data = new FormData();
    data.append('response', 'declined');
    data.append('user_id_from', user_id_from);
    data.append('user_id_to', user_id_to);

    request.send(data);
}