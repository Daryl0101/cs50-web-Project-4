document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#newpost-form-post').onclick = function() {
        post();
        return false;
    }
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