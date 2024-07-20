document.getElementById('comment-button').addEventListener('click', (e) => {
    e.target.style.color = "black"
    document.getElementById('info-button').style.color = "#BDBDBD"
    document.getElementById('info-part').style.display = "none"
    document.getElementById('comment-part').style.display = "block"
})

document.getElementById('info-button').addEventListener('click', (e) => {
    e.target.style.color = "black"
    document.getElementById('comment-button').style.color = "#BDBDBD"
    document.getElementById('info-part').style.display = "block"
    document.getElementById('comment-part').style.display = "none"
})