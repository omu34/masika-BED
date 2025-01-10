function scrollToSection() {
    const targetSection = document.getElementById('target-section');
    targetSection.scrollIntoView({
        behavior: 'smooth'
    });
}