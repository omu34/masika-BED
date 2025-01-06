const socket = io();

// Fetch and display initial articles
socket.on('initial_data', (data) => displayArticles(data));

// Handle updates for a specific type
socket.on('update_featured', ({ type, data }) => {
    const section = document.getElementById(`section-${type}`);
    if (section) {
        section.innerHTML = ''; // Clear
        displayArticles({ [type]: [data] });
    }
});

// Submit form to add an article
document.getElementById('article-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const articleType = formData.get('article_type');
    const response = await fetch(`/articles/update-article/${articleType}`, {
        method: 'POST',
        body: formData,
    });

    if (response.ok) {
        form.reset();
        alert('Article added!');
    } else {
        const error = await response.json();
        alert(error.error || 'Error occurred');
    }
});

async function toggleFeatured(type, id, isFeatured) {
    const response = await fetch(`/articles/toggle-featured/${type}/${id}`, {
        method: 'POST',
        body: JSON.stringify({ isFeatured }),
        headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) alert('Failed to toggle featured status');
}

async function deleteArticle(type, id) {
    const response = await fetch(`/articles/delete-article/${type}/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) alert('Failed to delete');
}

function displayArticles(data) {
    const container = document.getElementById('existing-articles');
    container.innerHTML = ''; // Clear articles

    for (const [type, articles] of Object.entries(data)) {
        const section = document.createElement('div');
        section.id = `section-${type}`;
        section.innerHTML = `<h3>${type.toUpperCase()}</h3>`;

        articles.forEach(article => {
            section.innerHTML += `
                <div class="border p-4">
                    <h4>${article.title}</h4>
                    <p>${article.description}</p>
                    <div>
                           <button class="mt-4 px-4 py-2 bg-green-500 bell-regular text-white hover:bg-green-700 rounded-lg" onclick="toggleFeatured('${type}', ${article.id}, true)">Feature</button>
                           <button class="mt-4 px-4 py-2 bg-yellow-500  bell-regular text-white hover:bg-yellow-700 rounded-lg" onclick="toggleFeatured('${type}', ${article.id}, false)">Unfeature</button>
                           <button class="mt-4 px-4 py-2 bg-red-500  bell-regular text-white hover:bg-red-700 rounded-lg" onclick="deleteArticle('${type}', ${article.id})">Delete</button>
                    </div>
                </div>
            `;
        });
        container.append(section);
    }
}