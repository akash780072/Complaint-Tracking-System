// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Real-time validation for registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        const inputs = registerForm.querySelectorAll('.form-control[required]');
        
        inputs.forEach(input => {
            input.addEventListener('input', () => validateInput(input));
            input.addEventListener('blur', () => validateInput(input));
        });

        // Double click to submit logic
        const submitBtn = document.getElementById('submitBtn');
        const confirmModal = document.getElementById('confirmModal');
        const modalOverlay = document.getElementById('modalOverlay');
        const cancelSubmit = document.getElementById('cancelSubmit');
        const confirmSubmit = document.getElementById('confirmSubmit');

        let isDoubleClick = false;

        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // In a real double click, the dblclick event will fire
            // but we can also simulate it or require double click directly.
        });

        submitBtn.addEventListener('dblclick', (e) => {
            e.preventDefault();
            if (validateForm(inputs)) {
                showModal();
            } else {
                alert('Please fill out all required fields correctly.');
            }
        });

        // Modal logic
        cancelSubmit.addEventListener('click', hideModal);
        
        confirmSubmit.addEventListener('click', () => {
            hideModal();
            submitForm();
        });

        function showModal() {
            modalOverlay.classList.add('active');
            setTimeout(() => confirmModal.classList.add('show'), 10);
        }

        function hideModal() {
            confirmModal.classList.remove('show');
            setTimeout(() => modalOverlay.classList.remove('active'), 300);
        }

        function submitForm() {
            const formData = new FormData(registerForm);
            
            fetch('/register', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Complaint Registered! Your tracking ID is: ' + data.complaint_id);
                    registerForm.reset();
                    inputs.forEach(i => {
                        i.classList.remove('valid');
                        i.classList.remove('invalid');
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        }
    }
    
    // Status update in admin dashboard
    const statusSelects = document.querySelectorAll('.select-status');
    statusSelects.forEach(select => {
        select.addEventListener('change', (e) => {
            const complaintId = e.target.dataset.id;
            const newStatus = e.target.value;
            
            const formData = new FormData();
            formData.append('id', complaintId);
            formData.append('status', newStatus);
            
            fetch('/admin/update_status', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Flash success or visually update
                    const tr = e.target.closest('tr');
                    tr.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
                    setTimeout(() => {
                        tr.style.backgroundColor = '';
                    }, 1000);
                } else {
                    alert('Error updating status');
                }
            });
        });
    });
});

function validateInput(input) {
    let errorMsg = input.nextElementSibling;
    if (errorMsg && !errorMsg.classList.contains('error-msg')) {
        errorMsg = null;
    }
    
    let isValid = true;

    if (input.value.trim() === '') {
        isValid = false;
        if(errorMsg) errorMsg.textContent = 'This field is required';
    } else if (input.type === 'email') {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = re.test(input.value);
        if(errorMsg) errorMsg.textContent = 'Please enter a valid email';
    }

    if (isValid) {
        input.classList.remove('invalid');
        input.classList.add('valid');
        if(errorMsg) errorMsg.style.display = 'none';
    } else {
        input.classList.remove('valid');
        input.classList.add('invalid');
        if(errorMsg) errorMsg.style.display = 'block';
    }
    
    return isValid;
}

function validateForm(inputs) {
    let isValid = true;
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    return isValid;
}
