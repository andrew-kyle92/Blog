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
    document.documentElement.scrollTop = 0;
}