document.addEventListener('scroll', function() {
    const heads = document.getElementById('heads');

    if (window.innerWidth > 768) { // Check if the screen width is greater than 768px
        if (window.scrollY > 0) {
            heads.style.backgroundColor = '#e6e5ff';
        } else {
            heads.style.backgroundColor = 'transparent';
        }
    } else {
        // On smaller screens (like mobile), the header will remain transparent
        heads.style.backgroundColor = '#e6e5ff';
    }
});

window.addEventListener('resize', function() {
    const heads = document.getElementById('heads');
    
    if (window.innerWidth <= 768) {
        // Ensure header is transparent when screen is resized to mobile view
        heads.style.backgroundColor = '#e6e5ff';
    }
});



