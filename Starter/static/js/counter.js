const targets = [
  { element: document.getElementById('starsCount'), count: 60, suffix: '+' },
  { element: document.getElementById('downloadsCount'), count: 550, suffix: '+' },
  { element: document.getElementById('sponsorsCount'), count: 46, suffix: '+' }
];

// Find the maximum count among all targets
const maxCount = Math.max(...targets.map(target => target.count));

// Function to animate count-up effect
function animateCountUp(target, duration) {
  let currentCount = 0;
  const increment = Math.ceil(target.count / (duration / 20));

  const interval = setInterval(() => {
      currentCount += increment;
      if (currentCount >= target.count) {
          clearInterval(interval);
          currentCount = target.count;
          target.element.textContent = currentCount + target.suffix;
      } else {
          target.element.textContent = currentCount;
      }
  }, 20);
}

// Create Intersection Observer to detect when counting section is in view
const observer = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
      if (entry.isIntersecting) {
          targets.forEach(target => {
              animateCountUp(target, maxCount / 1); // Adjust duration based on max count
          });
          observer.unobserve(entry.target); // Stop observing once animation starts
      }
  });
}, {
  threshold: 0.5 // Trigger when 50% of the section is in view
});

// Observe the section that contains the counters
const countingSection = document.getElementById('countingSection'); // Replace with your section's ID
observer.observe(countingSection);
