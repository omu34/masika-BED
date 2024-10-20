// Function to include HTML files
function loadHTML(file, elementId) {
    fetch(file)
        .then(response => response.text())
        .then(data => document.getElementById(elementId).innerHTML = data)
        .catch(error => console.error('Error loading HTML:', error));
}

// Load header and footer
loadHTML('header-h.html', 'header');
loadHTML('header-f.html', 'footer');