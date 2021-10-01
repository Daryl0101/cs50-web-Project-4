document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#all').addEventListener('click', () => load_view('all', 1));
    document.querySelector('#following').addEventListener('click', () => load_view('following', 1));
    document.querySelector('#profile').addEventListener('click', () => load_view('profile', 1));
    
    // Post form
    if(document.querySelector('#newpost-form-post')) {
        document.querySelector('#newpost-form-post').onclick = function() {
            post();
            window.location.reload();
        }
    }

    // Follow and unfollow button
    if(document.querySelector('.follow-button')) {
        document.querySelectorAll('.follow-button').forEach(button => {
            button.onclick = function() {
                update_follow(this);
            }
        });
    }

    // Like and unlike button
    if(document.querySelector('.post-likes')) {
        document.querySelectorAll('.post-likes').forEach(button => {
            button.onclick = function() {
                update_like(this);
            }
        });
    }

    // Edit button
    if(document.querySelector('.post-edit-button')){
        document.querySelectorAll('.post-edit-button').forEach(button => {
            button.onclick = function() {
                show_edit_textarea(this.parentNode.parentNode);
                this.parentNode.style.display = 'none';
                return false;
            }
        });
    }

    
    // Once the page renders, if there are edit buttons on the page, find the buttons
    // Function of the buttons:
    // onclick, hide the button (post-edit-button) and the content (post-content)
    // show (for-edit)
    // pre-fill (post-edit-textarea) with value of (post-content) or fetch the data to show
    // Set function of post button (post-edit-submit): once clicked, fetch 'PUT' and hid (for-edit)
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

function update_follow(button) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/update', {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            profile_user: button.dataset.info
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        button.innerText = result.btn_content;
        button.className = result.btn_class;
        document.querySelector('.followers').innerText = result.profile_followers;
    });
}

function update_like(button) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/update', {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            current_post: button.querySelector('.like-button').dataset.info
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        button.querySelector('.like-button').innerText = result.icon_html;
        button.querySelector('.post-likes-num').innerText = result.like_num;
    });
}

function show_edit_textarea(div){
    fetch(`/edit/${div.querySelector('.post-edit-button').dataset.id}`)
    .then(response => response.json())
    .then(result => {
        console.log(result);
        const element = document.createElement('div');
        element.className = 'for-edit';
        element.innerHTML = `<textarea class="post-edit-textarea form-control" rows="3">${result.content}</textarea><br>
        <button class="post-edit-submit btn btn-primary" data-id="${result.post_id}">Post</button>`;
        div.querySelector('.edit').append(element);
        // Post button after edit
        document.querySelector('.post-edit-submit').onclick = function() {
            edit(this.parentNode.parentNode.parentNode);
            this.parentNode.remove();
        }
    });
}

function edit(div) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/edit', {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            content: div.querySelector('.post-edit-textarea').value,
            post_id: div.querySelector('.post-edit-submit').dataset.id
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        if(result.content){
            div.querySelector('.post-content-edit-div').style.display = 'block';
            div.querySelector('.post-content').innerText = result.content;
        }
        else{
            alert(result.message);
            window.location.reload();
        }
    });
}