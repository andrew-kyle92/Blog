window.addEventListener("load", function(){
    var url = new URL(document.URL);
    var passChange = url.searchParams.get("pass_change_success");
    links = document.getElementById("sidebar");
    content = document.getElementsByClassName("cat-content")[0].children;
    if(url.toString().includes("pass_change_success")){
        links.children[1].classList.toggle("cat-active");
        content[1].style.display = "block";
    }
    else{
        links.children[0].classList.toggle("cat-active");
        content[0].style.display = "block";
    }
    links.addEventListener("click", function(e){
        for(let i = 0; i < links.children.length; i++){
            if(e.target.dataset["content"] == links.children[i].dataset["content"]){
                if(links.children[i].className.includes("active")){
                    links.children[i].classList.toggle("cat-active");
                    content[i].style.display = "none";
                }
                else{
                    links.children[i].classList.toggle("cat-active");
                    content[i].style.display = "block";
                }
            }
            else{
                links.children[i].classList.toggle("cat-active", false);
                content[i].style.display = "none";
            }
        }
    });
});