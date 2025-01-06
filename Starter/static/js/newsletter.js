
let button = document.getElementById("change-button");
let colors = [
    "red",
    "blue",
    "green",
    "yellow",
    "pink",
    "purple",
    "gray",
]; //Add more colors from tailwind design pallete as per requirement

function changeColor() {
    let color = colors[Math.floor(Math.random() * colors.length)];
    button.className = "";
    button.classList.add(
        "px-4",
        "py-2",
        "rounded-lg",
        "text-gray-800",
        `bg-${color}-500`
    );
}

setInterval(() => {
    changeColor();
}, 500); //Color change duration is 500 ms, you can adjust the duration.
