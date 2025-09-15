// API Base URL - Backend team se yeh URL milna chahiye
const API_BASE_URL = 'https://your-backend-api.com/api';

// DOM Elements
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const searchBtn = document.getElementById('searchBtn');
const searchInput = document.getElementById('searchInput');
const testLoginBtn = document.getElementById('testLoginBtn');
const loadInternshipsBtn = document.getElementById('loadInternshipsBtn');
const loginResponse = document.getElementById('loginResponse');
const internshipsResponse = document.getElementById('internshipsResponse');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Auth buttons
    loginBtn.addEventListener('click', handleLoginClick);
    registerBtn.addEventListener('click', handleRegisterClick);
    
    // Search functionality
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // API demo buttons
    testLoginBtn.addEventListener('click', testLoginAPI);
    loadInternshipsBtn.addEventListener('click', loadInternshipsAPI);
});

// Function to handle login click
function handleLoginClick() {
    alert('Login modal would open here.');
    // In a real application, this would open a login modal
}

// Function to handle register click
function handleRegisterClick() {
    alert('Registration page would open here.');
    // In a real application, this would redirect to registration page
}

// Function to handle search
function handleSearch() {
    const query = searchInput.value.trim();
    if (query !== '') {
        // In a real application, this would call the search API
        alert('Searching for: ' + query);
        
        // Example API call (commented out for now)
        // searchInternships(query);
    } else {
        alert('Please enter something to search.');
    }
}

// Function to test login API
async function testLoginAPI() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        loginResponse.textContent = 'Please enter both email and password';
        return;
    }
    
    loginResponse.textContent = 'Calling login API...';
    
    try {
        // This is a mock API call - replace with actual API endpoint
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        loginResponse.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        loginResponse.textContent = 'Error: ' + error.message;
        
        // For demo purposes, show mock response
        setTimeout(() => {
            loginResponse.textContent = JSON.stringify({
                success: true,
                message: 'Login successful',
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                user: {
                    id: 123,
                    name: 'Demo User',
                    email: email
                }
            }, null, 2);
        }, 1000);
    }
}

// Function to load internships API
async function loadInternshipsAPI() {
    internshipsResponse.textContent = 'Loading internships...';
    
    try {
        // This is a mock API call - replace with actual API endpoint
        const response = await fetch(`${API_BASE_URL}/internships`);
        const data = await response.json();
        internshipsResponse.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        internshipsResponse.textContent = 'Error: ' + error.message;
        
        // For demo purposes, show mock response
        setTimeout(() => {
            internshipsResponse.textContent = JSON.stringify({
                success: true,
                count: 3,
                internships: [
                    {
                        id: 1,
                        title: 'Software Development Intern',
                        department: 'Ministry of Electronics and IT',
                        location: 'New Delhi',
                        duration: '6 months',
                        skills: ['JavaScript', 'Python', 'React'],
                        match_score: 92
                    },
                    {
                        id: 2,
                        title: 'Data Analysis Intern',
                        department: 'NITI Aayog',
                        location: 'Remote',
                        duration: '3 months',
                        skills: ['Python', 'SQL', 'Data Visualization'],
                        match_score: 87
                    },
                    {
                        id: 3,
                        title: 'Policy Research Intern',
                        department: 'Ministry of Education',
                        location: 'New Delhi',
                        duration: '4 months',
                        skills: ['Research', 'Writing', 'Analysis'],
                        match_score: 78
                    }
                ]
            }, null, 2);
        }, 1000);
    }
}

// Example function to search internships (to be implemented)
async function searchInternships(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/internships/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        console.log('Search results:', data);
        // Process and display search results
    } catch (error) {
        console.error('Search error:', error);
    }
}

// Example function to get user profile (to be implemented)
async function getUserProfile(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Profile error:', error);
    }
}

// Utility function to display API responses
function displayResponse(element, data) {
    element.textContent = JSON.stringify(data, null, 2);
}
