 // Optional JavaScript for smoother animation
      // (consider using CSS animation for better performance)
      const slideContainer = document.querySelector('.slide-container');
      let currentSlide = 0;

      function slideLeft() {
        currentSlide++;
        slideContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
      }

      // Add event listeners for sliding (e.g., on hover or buttons)
      // slideLeft();