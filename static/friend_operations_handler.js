function blockFriend(user1_id, user2_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_operations');

    request.onload = () => {
        const data = JSON.parse(request.responseText);

    }

    const data = new FormData();
    data.append('operation', 'BLOCK');
    data.append('user1_id', user1_id);
    data.append('user2_id', user2_id);

    request.send(data);
}

function unblockFriend(user1_id, user2_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_operations');

    request.onload = () => {
        const data = JSON.parse(request.responseText);

    }

    const data = new FormData();
    data.append('operation', 'UNBLOCK');
    data.append('user1_id', user1_id);
    data.append('user2_id', user2_id);

    request.send(data);
}

function addFriendToFavourites(user1_id, user2_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_operations');

    request.onload = () => {
        const data = JSON.parse(request.responseText);

    }

    const data = new FormData();
    data.append('operation', 'FAVOURITE');
    data.append('user1_id', user1_id);
    data.append('user2_id', user2_id);

    request.send(data);
}

function removeFriendFromFavourites(user1_id, user2_id) {
    const request = new XMLHttpRequest();
    request.open('POST', '/profile/process_friend_operations');

    request.onload = () => {
        const data = JSON.parse(request.responseText);

    }

    const data = new FormData();
    data.append('operation', 'UNFAVOURITE');
    data.append('user1_id', user1_id);
    data.append('user2_id', user2_id);

    request.send(data);
}