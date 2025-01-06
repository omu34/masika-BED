let isPaused = false;

function scrollToSection(sectionId) {
    if (isPaused) return; // Prevent further actions during the 4-second pause

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        // Scroll instantly to the section
        targetSection.scrollIntoView({
            behavior: 'auto', // Instant scroll
            block: 'start'    // Scroll to the top of the section
        });

        // Pause user interaction for 4 seconds
        isPaused = true;
        setTimeout(() => {
            isPaused = false; // Re-enable interactions after 4 seconds
        }, 2000); // 4000ms = 4 seconds
    } else {
        console.error(`Section with ID ${sectionId} not found`);
    }
}