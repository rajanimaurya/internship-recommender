// Basic API demo functionality

// Login test
document.getElementById('testLoginBtn').addEventListener('click', function() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        document.getElementById('loginResponse').innerHTML = '<p style="color: #ff6b6b;">Please enter both email and password</p>';
        return;
    }
    
    document.getElementById('loginResponse').innerHTML = '<p>Simulating login API call...</p>';
    
    // Simulate API call
    setTimeout(() => {
        document.getElementById('loginResponse').innerHTML = `
            <p style="color: #00f5d4;">Login successful!</p>
            <p>Email: ${email}</p>
            <p>Redirecting to dashboard...</p>
        `;
    }, 1500);
});

// Load internships demo
document.getElementById('loadInternshipsBtn').addEventListener('click', function() {
    document.getElementById('internshipsResponse').innerHTML = '<p>Loading internships data...</p>';
    
    // Simulate API call
    setTimeout(() => {
        document.getElementById('internshipsResponse').innerHTML = `
            <h4>Available Internships:</h4>
            <ul>
                <li>Data Analyst - Ministry of Statistics</li>
                <li>Policy Research Intern - NITI Aayog</li>
                <li>Digital Marketing - MyGov</li>
                <li>Software Development - NIC</li>
            </ul>
        `;
    }, 1500);
});

// Upload resume demo (frontend only, no backend)
document.getElementById('uploadResumeDemoBtn').addEventListener('click', function() {
    const fileInput = document.getElementById('resumeFile');
    const file = fileInput.files[0];
    const uploadResponse = document.getElementById('uploadResponse');

    if (!file) {
        uploadResponse.innerHTML = '<p style="color: #ff6b6b;">Please select a file to upload</p>';
        return;
    }

    uploadResponse.innerHTML = '<p>Uploading...</p>';

    // Simulate upload
    setTimeout(() => {
        uploadResponse.innerHTML = `<p style="color: #00f5d4;">${file.name} uploaded successfully (demo)</p>`;
    }, 1200);
});

// Add hover stop functionality to marquee (kept for safety if CSS pause isn't enough)
const marqueeContainer = document.querySelector('.marquee-container');
const marquee = document.querySelector('.marquee');

if (marqueeContainer && marquee) {
    marqueeContainer.addEventListener('mouseenter', () => {
        marquee.style.animationPlayState = 'paused';
    });
    
    marqueeContainer.addEventListener('mouseleave', () => {
        marquee.style.animationPlayState = 'running';
    });
}

// Search button functionality
document.getElementById('searchBtn').addEventListener('click', function() {
    const searchTerm = document.getElementById('searchInput').value;
    if (searchTerm) {
        alert(`Searching for: ${searchTerm}`);
        // In a real application, this would trigger an API call
    } else {
        alert('Please enter a search term');
    }
});

// Login and Register button functionality
document.getElementById('loginBtn').addEventListener('click', function() {
    alert('Login dialog would appear here');
});

document.getElementById('registerBtn').addEventListener('click', function() {
    alert('Registration form would appear here');
});
