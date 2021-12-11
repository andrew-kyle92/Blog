function CloseMessage(){
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
    modalImg.src = this.src;
}

function SpanClick() {
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close-btn")[0];

    // When the user clicks on <span> (x), close the modal
    modal.style.display = "none";
}