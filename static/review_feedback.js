function toggle_like(x) {
	if(x.innerHTML === "Like"){
        x.innerHTML="You Liked It";
        document.getElementById(x.value+"d").disabled = true;
    }
    else{
        x.innerHTML="Like";
        document.getElementById(x.value+"d").disabled = false;
    }
}

function toggle_dislike(x) {
	if(x.innerHTML === "Dislike"){
           x.innerHTML="You Disliked It";
           document.getElementById(x.value+"l").disabled = true;
    }
    else{
        x.innerHTML="Dislike";
        document.getElementById(x.value+"l").disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('.likes').forEach(function(button) {
        button.onclick = function() {
            const request = new XMLHttpRequest();
            const like_sit = button.innerHTML;
            request.open('POST', '/process_likes_dislikes/');

            request.onload = () => {

                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                if (data.success) {
                    toggle_like(button);
                    document.getElementById(button.value+"l").disabled = false;
                }
            }
            const data = new FormData();
            data.append('entity_id', button.value);
            data.append('sit4process', "like");
            data.append('like_sit', like_sit);
            data.append('entity_type', button.dataset.ent_type);
            document.getElementById(button.value+"l").disabled = true;
            document.getElementById(button.value+"d").disabled = true;
    
            // Send request
            request.send(data);
            return false;
        };
    });
});


document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('.dislikes').forEach(function(button) {
        button.onclick = function() {
            const request = new XMLHttpRequest();
            const disl_sit = button.innerHTML;
            request.open('POST', '/process_likes_dislikes/');

            request.onload = () => {

                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                if (data.success) {
                    toggle_dislike(button);
                    document.getElementById(button.value+"d").disabled = false;
                }
            }
            const data = new FormData();
            data.append('entity_id', button.value);
            data.append('sit4process', "dislike");
            data.append('disl_sit', disl_sit);
            data.append('entity_type', button.dataset.ent_type);
            document.getElementById(button.value+"d").disabled = true;
            document.getElementById(button.value+"l").disabled = true;
    
            // Send request
            request.send(data);
            return false;
        };
    });
});


