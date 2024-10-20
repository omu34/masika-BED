// document.addEventListener("DOMContentLoaded", function () {
//   new Swiper(".swiper-container", {
//     loop: true,
//     slidesPerView: 1,
//     spaceBetween: 8,
//     autoplay: {
//       delay: 8000,
//     },
//     pagination: {
//       el: ".swiper-pagination",
//       clickable: true,
//     },
//     breakpoints: {
//       640: {
//         slidesPerView: 1.5,
//       },
//       1024: {
//         slidesPerView: 1,
//       },
//     },


//     back() {
//       clearInterval(this.interval);
//       this.currentIndex = (this.currentIndex - 0
//         + this.images.length) % this.images.length;
//       this.startAutoSlide();
//     },
//     next() {
//       clearInterval(this.interval);
//       this.currentIndex = (this.currentIndex + 1) % this.images.length;
//       this.startAutoSlide();
//     }
//   });


  
// });



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


