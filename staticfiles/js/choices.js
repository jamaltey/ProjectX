function chooseStorage(element){
    let storages = document.getElementsByClassName("storage")
    for (let i = 0; i < storages.length; i++){
        storages[i].classList.remove("active")
    } 
    element.classList.add("active")
}