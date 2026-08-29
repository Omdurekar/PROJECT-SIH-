let slideIndex = 0;

const slides = document.querySelectorAll(".slide");

function showSlide(index) {

    slides.forEach(slide => {
        slide.classList.remove("active");
    });

    slides[index].classList.add("active");
}


// Automatically change slide every 5 seconds
setInterval(() => {

    slideIndex++;

    if (slideIndex >= slides.length) {
        slideIndex = 0;
    }

    showSlide(slideIndex);

}, 5000);


// Show first slide
showSlide(slideIndex);
// ==========================================
// AUTOMATIC IMAGE SLIDER
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");

    let slideIndex = 0;

    // If no slides are found
    if (slides.length === 0) {
        console.log("ERROR: No .slide elements found");
        return;
    }

    function showSlide(index) {

        // Remove active from all slides
        slides.forEach(function (slide) {
            slide.classList.remove("active");
        });

        // Remove active from all dots
        dots.forEach(function (dot) {
            dot.classList.remove("active");
        });

        // Show selected slide
        slides[index].classList.add("active");

        // Activate corresponding dot
        if (dots[index]) {
            dots[index].classList.add("active");
        }
    }


    // ======================================
    // AUTOMATICALLY CHANGE EVERY 5 SECONDS
    // ======================================

    setInterval(function () {

        slideIndex++;

        if (slideIndex >= slides.length) {
            slideIndex = 0;
        }

        showSlide(slideIndex);

    }, 5000);


    // Show first slide
    showSlide(0);


    // ======================================
    // MAKE DOTS CLICKABLE
    // ======================================

    dots.forEach(function (dot, index) {

        dot.addEventListener("click", function () {

            slideIndex = index;

            showSlide(slideIndex);

        });

    });

});