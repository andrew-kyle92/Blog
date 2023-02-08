// For the scrolling capabilities
var scrollBtn = document.getElementById("scrollToTop");
window.onscroll = function() {scrollFunction()};

function scrollFunction(){
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20){
        scrollBtn.style.display = "block";
    } else {
        scrollBtn.style.display = "none";
    }
}

function topFunction(){
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Nav menu responsiveness
var mobileHeader = document.getElementById("mobile-header");
var nonMobileHeader = document.getElementById("page-top");

if(window.innerWidth < 700){
    nonMobileHeader.style.display = "none";
    mobileHeader.style.display = "flex";
}
else{
    nonMobileHeader.style.display = "flex"
    mobileHeader.style.display = "none";
}

this.window.addEventListener("resize", function(){
    if(this.innerWidth < 700){
        nonMobileHeader.style.display = "none";
        mobileHeader.style.display = "flex";
    }
    else{
        nonMobileHeader.style.display = "flex"
        mobileHeader.style.display = "none";
    }
});

// Menu button login
var menuBtn = document.getElementsByClassName("nav-menu-btn")[0];
var content = document.getElementsByClassName("links-content")[0];

menuBtn.addEventListener("click", function(){
    if(!menuBtn.className.includes("active")){
        menuBtn.classList.add("active");
        content.style.maxHeight = content.scrollHeight + "px";
    }
    else{
        menuBtn.classList.remove("active");
        content.style.maxHeight = null;
    }
});
