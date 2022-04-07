function closeMessage(){
    var message = document.querySelector(".email-success");
    message.remove()
}

function image(){
    // Get the modal
    var modal = document.getElementById("img-popup");

    // Get the image and insert it inside the modal - use its "alt" text as a caption
    var img = document.getElementById("profileImg");
    var modalImg = document.getElementById("img01");

    modal.style.display = "block";
    modalImg.setAttribute("src", img.getAttribute("src"));
}

function spanClick() {
    // Get the modal
    var modal = document.getElementById("img-popup");
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close-btn")[0];

    // When the user clicks on <span> (x), close the modal
    modal.style.display = "none";
}

function edit() {
    var editBtns = document.getElementsByClassName("edit-btn");
    var textEdit = document.getElementsByClassName("pro-cont-edit");
    for(let i = 0; i < editBtns.length; i++){
        if(e.target.parentElement == editBtns[i]){
            console.log(editBtns[i]);
            console.log(textEdit[i]);
        }
    }
}

// For Song Upload page
window.addEventListener("load", () => {
    submitBtn = document.getElementById("submit");
    if(document.URL.includes("song-upload")){
        submitBtn.addEventListener("click", () => {
            for(let i = 0; i < 60; i++)
                setTimeout(() => {
                    if(submitBtn.value == "Loading"){
                        submitBtn.value = "Loading."
                    }
                    else if(submitBtn.value == "Loading."){
                        submitBtn.value = "Loading.."
                    }
                    else if(submitBtn.value == "Loading.."){
                        submitBtn.value = "Loading..."
                    }
                    else{
                        submitBtn.value = "Loading"
                    }
                }, 100)
        });
    }
});

// Show/Hide password
var allEyes = document.getElementsByClassName("show-pass");
for(let i = 0; i < allEyes.length; i++){
    let input = allEyes[i].previousElementSibling;
    let eyeSlash = "fas fa-regular fa-eye-slash";
    let openEye = "fas fa-regular fa-eye";
    allEyes[i].addEventListener("click", function(){
        if(allEyes[i].children[0].className == openEye){
            allEyes[i].children[0].setAttribute("class", eyeSlash);
            input.setAttribute("type", "text");
        }
        else{
            allEyes[i].children[0].setAttribute("class", openEye);
            input.setAttribute("type", "password");
        }
    });
}