function toggle_like(x) {
	if(x.innerHTML === "Like"){
        x.innerHTML="You Liked It";
        document.getElementById("disl_sub").disabled = true;
    }
    else{
        x.innerHTML="Like";
        document.getElementById("disl_sub").disabled = false;
    }
}

function toggle_dislike(x) {
	if(x.innerHTML === "Dislike"){
           x.innerHTML="You Disliked It";
           document.getElementById("like_sub").disabled = true;
    }
    else{
        x.innerHTML="Dislike";
        document.getElementById("like_sub").disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('#like').onclick = () => {

        const request = new XMLHttpRequest();
        const like_sit = document.querySelector('#like_sub').innerHTML;
        request.open('POST', '/process_review_feedback/');

        request.onload = () => {

            // Extract JSON data from request
            const data = JSON.parse(request.responseText);
            if (data.success) {
                toggle_like(document.querySelector('#like_sub'));
                document.getElementById("like_sub").disabled = false;
            }
        }
        const data = new FormData();
        data.append('review_id', document.querySelector('#like_sub').value);
        data.append('sit4process', "like")
        data.append('like_sit', like_sit);
        document.getElementById("like_sub").disabled = true;

        // Send request
        request.send(data);
        return false;
    };
});

document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('#dislike').onclick = () => {

        const request = new XMLHttpRequest();
        const disl_sit = document.querySelector('#disl_sub').innerHTML;
        request.open('POST', '/process_review_feedback/');

        request.onload = () => {

            // Extract JSON data from request
            const data = JSON.parse(request.responseText);
            if (data.success) {
                toggle_dislike(document.querySelector('#disl_sub'));
                document.getElementById("disl_sub").disabled = false;
            }
        }
        const data = new FormData();
        data.append('review_id', document.querySelector('#disl_sub').value);
        data.append('sit4process', "dislike")
        data.append('disl_sit', disl_sit);
        
        document.getElementById("disl_sub").disabled = true;
        // Send request
        request.send(data);
        return false;
    };
});
