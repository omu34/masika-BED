document.getElementById("hamburger").onclick = function toggleMenu() {
    const navToggle = document.querySelectorAll(".toggle");
    navToggle.forEach(element => {
        element.classList.toggle("hidden");
    });
};
