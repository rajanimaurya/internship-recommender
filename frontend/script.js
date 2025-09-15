// DOM Elements
const fileInput = document.getElementById('fileInput');
const cameraBtn = document.getElementById('cameraBtn');
const cameraFeed = document.getElementById('cameraFeed');
const video = document.getElementById('video');
const captureBtn = document.getElementById('captureBtn');
const dropZone = document.getElementById('dropZone');
const selectedFileContainer = document.getElementById('selectedFileContainer');
const selectedFileName = document.getElementById('selectedFileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loading');
const resultsSection = document.getElementById('results');
const profileSummary = document.getElementById('profileSummary');
const recommendations = document.getElementById('recommendations');
const skillsContainer = document.getElementById('skillsContainer');
const internshipsContainer = document.getElementById('internshipsContainer');

// State variables
let stream = null;
let selectedFile = null;

// Event Listeners
document.addEventListener('DOMContentLoaded', init);

function init() {
    // Initialize drag and drop
    initDragAndDrop();
    
    // Initialize camera functionality
    initCamera();
    
    // Initialize analyze button
    analyzeBtn.addEventListener('click', analyzeResume);
}

// Drag and Drop functionality
function initDragAndDrop() {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#4361ee';
        dropZone.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#4361ee';
        dropZone.style.backgroundColor = 'rgba(67, 97, 238, 0.05)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#4361ee';
        dropZone.style.backgroundColor = 'rgba(67, 97, 238, 0.05)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });
}

// Camera functionality
function initCamera() {
    cameraBtn.addEventListener('click', openCamera);
    captureBtn.addEventListener('click', captureImage);
}

async function openCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        cameraFeed.classList.remove('hidden');
        cameraBtn.classList.add('hidden');
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert('Unable to access camera. Please check permissions.');
    }
}

function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Stop the video stream
    stream.getTracks().forEach(track => track.stop());
    
    // Convert canvas to blob and create a file
    canvas.toBlob((blob) => {
        const file = new File([blob], 'resume-photo.jpg', { type: 'image/jpeg' });
        handleFileSelection(file);
        
        // Reset camera UI
        cameraFeed.classList.add('hidden');
        cameraBtn.classList.remove('hidden');
    }, 'image/jpeg');
}

// File handling
function handleFileSelection(file) {
    selectedFile = file;
    selectedFileName.textContent = file.name;
    selectedFileContainer.classList.remove('hidden');
    
    // Check file type
    const fileType = file.type;
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                        'application/msword', 'text/plain', 'image/jpeg', 'image/png'];
    
    if (!validTypes.includes(fileType)) {
        alert('Please upload a valid file type (PDF, DOCX, DOC, TXT, JPG, PNG)');
        selectedFile = null;
        selectedFileContainer.classList.add('hidden');
        return;
    }
}

// Analyze resume
function analyzeResume() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    // Show loading state
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    // Simulate processing delay
    setTimeout(() => {
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        generateResults();
    }, 2500);
}

// Generate results
function generateResults() {
    // Sample data for demonstration
    const sampleSkills = ['JavaScript', 'React', 'HTML5', 'CSS3', 'Python', 'Node.js', 'UI/UX Design', 'Git'];
    const sampleSummary = "Based on your resume, our AI has identified strong skills in frontend development with experience in React and JavaScript. Your profile shows potential for roles in web development, UI engineering, and full-stack development.";
    
    const sampleInternships = [
        {
            title: "Frontend Development Intern",
            company: "Tech Innovations Inc.",
            match: 92,
            skills: ["HTML", "CSS", "JavaScript", "React"],
            description: "Join our frontend team to build responsive web applications using modern frameworks.",
            location: "Remote",
            duration: "3 months",
            stipend: "$2,000/month",
            applyLink: "#"
        },
        {
            title: "UX/UI Design Intern",
            company: "Creative Solutions",
            match: 85,
            skills: ["Figma", "UI Design", "Wireframing", "User Research"],
            description: "Work with our design team to create intuitive user interfaces for our products.",
            location: "New York, NY",
            duration: "4 months",
            stipend: "$1,800/month",
            applyLink: "#"
        },
        {
            title: "Full Stack Developer Intern",
            company: "WebCraft Studios",
            match: 88,
            skills: ["JavaScript", "Node.js", "React", "MongoDB"],
            description: "Develop end-to-end web applications in a collaborative agile environment.",
            location: "San Francisco, CA",
            duration: "6 months",
            stipend: "$2,500/month",
            applyLink: "#"
        },
        {
            title: "Software Engineering Intern",
            company: "DataDrive Technologies",
            match: 79,
            skills: ["Python", "Java", "SQL", "Data Structures"],
            description: "Work on backend systems and data processing pipelines for our analytics platform.",
            location: "Austin, TX",
            duration: "5 months",
            stipend: "$2,200/month",
            applyLink: "#"
        }
    ];
    
    // Display skills
    skillsContainer.innerHTML = '';
    sampleSkills.forEach(skill => {
        const skillElement = document.createElement('span');
        skillElement.className = 'skill-tag';
        skillElement.textContent = skill;
        skillsContainer.appendChild(skillElement);
    });
    
    // Display profile summary
    profileSummary.textContent = sampleSummary;
    
    // Display recommended internships
    internshipsContainer.innerHTML = '';
    sampleInternships.forEach(internship => {
        const internshipElement = document.createElement('div');
        internshipElement.className = 'internship-card';
        internshipElement.innerHTML = `
            <div class="internship-header">
                <h3>${internship.title}</h3>
                <span class="match-badge">${internship.match}% Match</span>
            </div>
            <p class="company-name">${internship.company}</p>
            <p class="internship-description">${internship.description}</p>
            <div class="internship-details">
                <div class="detail">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${internship.location}</span>
                </div>
                <div class="detail">
                    <i class="fas fa-clock"></i>
                    <span>${internship.duration}</span>
                </div>
                <div class="detail">
                    <i class="fas fa-money-bill-wave"></i>
                    <span>${internship.stipend}</span>
                </div>
            </div>
            <div class="skills-container">
                ${internship.skills.map(skill => `<span class="skill-tag small">${skill}</span>`).join('')}
            </div>
            <a href="${internship.applyLink}" class="apply-btn">Apply Now</a>
        `;
        internshipsContainer.appendChild(internshipElement);
    });
    
    // Generate recommendations
    recommendations.innerHTML = `
        <h3>Career Development Recommendations</h3>
        <ul>
            <li>Consider building a portfolio website to showcase your projects</li>
            <li>Contribute to open-source projects to gain collaborative experience</li>
            <li>Learn about backend technologies to become a full-stack developer</li>
            <li>Practice algorithm problems on platforms like LeetCode</li>
            <li>Attend local tech meetups or virtual conferences to network</li>
        </ul>
    `;
}
