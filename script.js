const images = [
    "images/image2.jpg",
    "images/image3.jpg",
    "images/image4.jpg",
    "images/image5.jpg"
];

let currentImage = 0;

const hero = document.querySelector(".hero");
const dots = document.querySelectorAll(".dot");


function showImage(index) {

    currentImage = index;

    hero.style.backgroundImage =
        `linear-gradient(
            rgba(0, 0, 0, 0.25),
            rgba(0, 0, 0, 0.25)
        ),
        url("${images[currentImage]}")`;

    dots.forEach(dot => {
        dot.classList.remove("active");
    });

    dots[currentImage].classList.add("active");
}


function nextImage() {

    currentImage++;

    if (currentImage >= images.length) {
        currentImage = 0;
    }

    showImage(currentImage);
}


function previousImage() {

    currentImage--;

    if (currentImage < 0) {
        currentImage = images.length - 1;
    }

    showImage(currentImage);
}


/* Automatically change every 5 seconds */

setInterval(nextImage, 5000);