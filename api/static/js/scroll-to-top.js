function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.addEventListener('scroll', () => {
    const scrollTopButton = document.getElementById('scrollToTopButton');
    if (window.scrollY > 100) {
        scrollTopButton.classList.add('show');
        scrollTopButton.classList.remove('hidden');
    } else {
        scrollTopButton.classList.remove('show');
        scrollTopButton.classList.add('hidden');
    }
});