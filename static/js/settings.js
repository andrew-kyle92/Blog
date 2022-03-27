window.addEventListener("load", function(){

    links = document.getElementById("sidebar");
    content = document.getElementsByClassName("cat-content")[0].children;
    links.children[0].classList.toggle("cat-active");
    content[0].style.display = "block";
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

    // // Show/Hide password
    // var allEyes = document.getElementsByClassName("show-pass");
    // for(let i = 0; i < allEyes.length; i++){
    //     let input = allEyes[i].previousElementSibling;
    //     let eyeSlash = "fas fa-regular fa-eye-slash";
    //     let openEye = "fas fa-regular fa-eye";
    //     allEyes[i].addEventListener("click", function(){
    //         if(allEyes[i].children[0].className == openEye){
    //             allEyes[i].children[0].setAttribute("class", eyeSlash);
    //             input.setAttribute("type", "text");
    //         }
    //         else{
    //             allEyes[i].children[0].setAttribute("class", openEye);
    //             input.setAttribute("type", "password");
    //         }
    //     });
    // }
});