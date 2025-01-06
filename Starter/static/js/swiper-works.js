

var swiper6 = new Swiper(".mySwiperSlides", {
    loop: true,
    grabCursor: true,
    clickable: true,
    effect: "creative",
    speed: 7000, // Slow down the transition speed to 2 seconds
    pagination: {
        el: ".swiper-pagination",
    },
    autoplay: {
        delay: 8000, // Increase autoplay delay to 12 seconds
        disableOnInteraction: false,
    },
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    creativeEffect: {
        prev: {
            shadow: true,
            origin: 'left center',
            translate: ['-10%', 0, -300],
            scale: [0.8, 1],
            opacity: [0, 1],
        },
        next: {
            origin: 'right center',
            translate: ['10%', 0, -300],
            scale: [1, 0.8],
            opacity: [1, 0],
        },
    },
});





document.addEventListener("DOMContentLoaded", function () {
    const swiper = new Swiper(".swiper-container", {
        // ... other Swiper configuration options
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
    });

    // Manually trigger navigation on button click (if needed)
    document.querySelector('.swiper-button-prev').addEventListener('click', function () {
        swiper.slidePrev();
    });

    document.querySelector('.swiper-button-next').addEventListener('click', function () {
        swiper.slideNext();
    });
});