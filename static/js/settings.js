window.addEventListener("load", function(){
    links = document.getElementById("sidebar");
    content = document.getElementsByClassName("cat-content")[0].children;
    links.children[0].classList.toggle("cat-active");
    content[0].style.display = "block";
    links.addEventListener("click", function(e){
        for(let i = 0; i < links.children.length; i++){
            if(e.target.dataset["content"] == links.children[i].dataset["content"]){
                links.children[i].classList.toggle("cat-active");
                content[i].style.display = "block";
            }
            else{
                links.children[i].classList.toggle("cat-active", false);
                content[i].style.display = "none";
            }
        }
    });
});