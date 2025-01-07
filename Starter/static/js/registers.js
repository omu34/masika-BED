
    function toggleAdminCodeField() {
        var adminCheckbox = document.getElementById('is_admin');
    var adminCodeField = document.getElementById('admin_code_field');
    if (adminCheckbox.checked) {
        adminCodeField.style.display = 'block'; // Show the admin code field when checkbox is checked
    document.getElementById('admin_code').required = true; // Make admin code required
        } else {
        adminCodeField.style.display = 'none';  // Hide the admin code field when checkbox is unchecked
    document.getElementById('admin_code').required = false; // Remove required attribute
        }
    }



    


