 var swiper6 = new Swiper(".mySwiperSlides", {
            loop: true,
            on: {
                slideChangeTransitionEnd: function () {
                    AOS.refreshHard(); // More aggressive refresh
                }
            }
        });


        AOS.init({
            duration: 400, // Adjust as needed for effect duration
            once: true,     // Only animate once
        });
