document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#all').addEventListener('click', () => load_view('all', 1));
    document.querySelector('#following').addEventListener('click', () => load_view('following', 1));
    document.querySelector('#profile').addEventListener('click', () => load_view('profile', 1));
    
    /* document.querySelectorAll('li.prev').forEach(item => item.style.display = 'none');
    document.querySelectorAll('li.nxt').forEach(item => item.style.display = 'none'); */
    
    if(document.querySelector('#newpost-form-post')) {
        document.querySelector('#newpost-form-post').onclick = function() {
            post();
            window.location.reload();
        }
    }

    if(document.querySelector('.follow-button')) {
        profile_user = document.querySelector('.follow-button').dataset.info;
        document.querySelector('.follow-button').addEventListener('click', function(){
            update_follow('follow', profile_user);
            window.location.reload();
        });
    }
    else if(document.querySelector('.unfollow-button')) {
        profile_user = document.querySelector('.unfollow-button').dataset.info;
        document.querySelector('.unfollow-button').addEventListener('click', function(){
            update_follow('unfollow', profile_user);
            window.location.reload();
        });
    }
    /* load_view('all', 1); */
});

function post() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch("/network", {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            content: document.querySelector('#newpost-form-text').value
        })
    })
    .then(response => response.json())
    .then(result => {
        if(result.message){
            alert(result.message)
        }
        else{
            alert(result.error)
        }
    });
    document.querySelector('#newpost-form-text').value = "";
}

function update_follow(type, profile_user) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if(type=='follow'){
        follow_status = true;
    }
    else {
        follow_status = false;
    }
    fetch(`/updatefollow`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            toFollow: follow_status,
            profile_user: profile_user
        })
    })
    .then(response => response.json())
    .then(result => console.log(result));
}

/* function load_view(view, page) {
    
    fetch(`/network/${view}/${page}`)
    .then(response => response.json())
    .then(page_in => {
        console.log(page_in);
        load_pagebar(page_in);
    })
    .catch(error => console.error(`Unable to fetch items for ${view}: Page ${page}`, error));
} */

/* function load_pagebar(page_fetched){
    // Hide all previous and next buttons
    document.querySelectorAll('li.prev').forEach(item => item.style.display = 'none');
    document.querySelectorAll('li.nxt').forEach(item => item.style.display = 'none');
    
    console.log(`Previous page: ${page_fetched.post_type, page_fetched.previous_page_number}`);
    console.log(`Next page: ${page_fetched.post_type, page_fetched.next_page_number}`);

    if(page_fetched.has_previous == true){
        document.querySelector('li.prev.enabled').style.display = 'block';
        document.querySelector('li.prev.enabled').addEventListener('click', () => {
            load_view(page_fetched.post_type, page_fetched.previous_page_number);
            console.log('Previous button clicked');
        });
    }
    else if(page_fetched.has_previous == false){
        document.querySelector('li.prev.disabled').style.display = 'block';
    }

    if(page_fetched.has_next == true){
        document.querySelector('li.nxt.enabled').style.display = 'block';
        document.querySelector('li.nxt.enabled').addEventListener('click', () => {
            load_view(page_fetched.post_type, page_fetched.next_page_number);
            console.log('Next button clicked');
        });
    }
    else if(page_fetched.has_next == false){
        document.querySelector('li.nxt.disabled').style.display = 'block';
    }
} */