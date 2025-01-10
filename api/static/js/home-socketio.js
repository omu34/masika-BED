const socket = io();

// Load articles on connection
socket.on('initial_data', (data) => {
    displayArticles(data);
});

// Listen for updates
socket.on('update_featured', ({ type, data }) => {
    const updatedSection = { [type]: data };
    displayArticles(updatedSection, true); // Partial update
});

function renderMedia(link) {
    // Check if the link is a YouTube video
    const youtubeMatch = link.match(/(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([\w-]+)/) ||
        link.match(/(?:https?:\/\/)?youtu\.be\/([\w-]+)/);
    if (youtubeMatch) {
        const videoId = youtubeMatch[1];
        return `<iframe width="360" height="205" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>`;
    }

    // Check if the link is an image (ends with common image extensions)
    const imageMatch = link.match(/\.(jpeg|jpg|gif|png|webp)$/i);
    if (imageMatch) {
        return `<img src="${link}" alt="Article Image" class="w-full max-h-[205px] object-cover">`;
    }

    // Check if the link is a video file (ends with video extensions)
    const videoMatch = link.match(/\.(mp4|mov|avi|mkv|webm)$/i);
    if (videoMatch) {
        return `<video controls class="w-full max-h-80">
                        <source src="${link}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>`;
    }

    // If it's not an image, YouTube video, or video file, just link it
    return `<a href="${link}" target="_blank" class="text-blue-500 underline">${link}</a>`;
}

function displayArticles(featuredArticles, isPartialUpdate = false) {
    for (const [type, articles] of Object.entries(featuredArticles)) {
        let sectionElement = document.getElementById(type);

        // If section does not exist and it's not a partial update, create it
        if (!sectionElement && !isPartialUpdate) {
            sectionElement = document.createElement('div');
            sectionElement.id = type;
            sectionElement.innerHTML = `<h2 class="text-xl bell text-red-900 font-bold mb-4">${type.toUpperCase()}</h2>`;
            document.getElementById('featured-articles').appendChild(sectionElement);
        }

        // Clear section content on partial update to avoid duplicate entries
        if (isPartialUpdate) {
            sectionElement.innerHTML = `<h2 class="text-xl font-bold mb-4">${type.toUpperCase()}</h2>`;
        }

        // Render articles
        articles.forEach((article, index) => {
            const articleHTML = `
                    <div class="p-4 bg-white shadow mb-4">
                        <h3 class="text-lg bell-bold font-bold text-red-800">${article.title || 'Untitled'}</h3>
                        <p class="bell-regular text-gray-900 text-md">${article.description || 'No description available.'}</p>
                        <p class="text-sm bell text-blue-700">Featured At: ${article.time_featured}</p>
                        <p class="text-sm bell text-red-700">Time to Read: ${article.time_to_read}</p>
                        ${renderMedia(article.link)}
                        <button class="mt-4 px-4 py-2 bell text-md bg-yellow-500 text-white rounded"
                                onclick="('${type}', ${index}, ${!article.is_featured})">
                            ${article.is_featured ? 'Unfeature' : 'Featured'}
                        </button>
                    </div>
                `;
            sectionElement.innerHTML += articleHTML;
        });
    }
}

async function toggleFeatured(type, index, isFeatured) {
    try {
        const response = await fetch(`/realtime/toggle-featured/${type}/${index}`, {
            method: 'POST',
            body: JSON.stringify({ isFeatured }),
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            alert(isFeatured ? 'Article featured!' : 'Article unfeatured!');
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to update feature status.');
        }
    } catch (error) {
        alert('An error occurred while updating feature status.');
    }
}



document.getElementById('article-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    const link = formData.get('link');
    const file = formData.get('file');

    // Ensure either link or file is provided, but not both
    if (link && file.size > 0) {
        alert('Please provide either a video link or upload a video file, but not both.');
        return;
    }

    if (!link && file.size === 0) {
        alert('Please provide a video link or upload a video file.');
        return;
    }

    try {
        const articleType = formData.get('article_type');
        const response = await fetch(`/realtime/add-article/${articleType}`, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            form.reset();
            alert('Video added successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.message}`);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('An error occurred. Please try again.');
    }
});