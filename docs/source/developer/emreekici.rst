Parts Implemented by Ömer Emre Ekici
====================================
For this project, I have worked on the tables GAMES, GAMES_OF_USERS &
FRIENDS, FRIEND_REQUESTS, PROFILE_PHOTOS, BALANCE_CODES, RATING_VOTES
and their related functions.

Database Design
---------------

.. image:: diagram_emre.jpeg
    :width: 600

* The "GAMES" table contains the games available on the website.
* The "GAMES_OF_USERS" table contains the games owned by a user.
* The "FRIENDS" table contains the data of two users who are friends.
* The "FRIEND_REQUESTS" table contains the requests sent by a user
  to another user.
* The "PROFILE_PHOTOS" table contains the user's profile photo data.
* The "RATING_VOTES" table contains the ratings a user made for each
  game.

Code
----
Database Functions
~~~~~~~~~~~~~~~~~~
.. automodule:: database_emre
    :members: Database

Server Functions
~~~~~~~~~~~~~~~~
.. automodule:: server_emre
    :members: Server

Javascript Functions
~~~~~~~~~~~~~~~~~~~~

**friend_operations_handler**

::

    function removeFriend(user1_id, user2_id) {
        const request = new XMLHttpRequest();
        request.open('POST', '/profile/process_friend_operations');

        request.onload = () => {
            const data = JSON.parse(request.responseText);
            document.getElementById('remove_friend').innerHTML = data.responseText
        }

        const data = new FormData();
        data.append('operation', 'REMOVE');
        data.append('user1_id', user1_id);
        data.append('user2_id', user2_id);

        request.send(data);
    }

Sends the request to remove the friend of a user to the webpage and
displays the result of the operation to the user.

::

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

Sends the request to block the friend of a user to the webpage and
displays the result of the operation to the user.

::

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

Sends the request to unblock the friend of a user to the webpage and
displays the result of the operation to the user.

::

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

Sends the request to favourite the friend of a user to the webpage
and displays the result of the operation to the user.

::

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

Sends the request to unfavourite the friend of a user to the webpage
and displays the result of the operation to the user.

**friend_request_feedback**

::

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

Sends the request to cancel the friend request of a user to the
webpage and displays the result of the operation to the user.

::

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

Sends the request to accept the friend request of a user to the
webpage and displays the result of the operation to the user.

::

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

Sends the request to decline the friend request of a user to the
webpage and displays the result of the operation to the user.

**game_favouriting_handler**

::

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

Sends the request to favourite the game of a user to the webpage
and displays the result of the operation to the user.

::

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

Sends the request to unfavourite the game of a user to the webpage
and displays the result of the operation to the user.

**play_game_handler**

::

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

Send the data about the game the user have played and the play time
they have on the game to be processed by the webpage and reloads the
play time on the user's profile.