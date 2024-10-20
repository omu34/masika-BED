// JavaScript to toggle the modal
const openContactFormButton = document.getElementById('openContactForm');
const closeContactFormButton = document.getElementById('closeContactForm');
const contactFormModal = document.getElementById('contactFormModal');

openContactFormButton.addEventListener('click', () => {
    contactFormModal.classList.remove('hidden');
});

closeContactFormButton.addEventListener('click', () => {
    contactFormModal.classList.add('hidden');
});