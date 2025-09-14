import re
import docx
import logging
from PyPDF2 import PdfReader
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined list of technical skills with categories
SKILLS_DB = {
    "Programming Languages": ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "PHP", "Ruby", "Go", "Rust", "Swift", "Kotlin"],
    "Web Technologies": ["HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "Express.js", "jQuery"],
    "Databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQLite", "Cassandra"],
    "Data Science & AI": ["Machine Learning", "Deep Learning", "Data Science", "NLP", "Computer Vision", "TensorFlow", "Keras", "PyTorch", "Pandas", "NumPy", "SciPy", "Scikit-learn"],
    "DevOps & Cloud": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "Git", "Linux", "Bash"],
    "Mobile Development": ["Android", "iOS", "React Native", "Flutter", "Xamarin"],
    "Other": ["REST API", "GraphQL", "Microservices", "Agile", "Scrum", "TDD", "OOP"]
}

# Education patterns
EDUCATION_PATTERNS = [
    r"(Bachelor|B\.?Tech|B\.?E|Master|M\.?Tech|M\.?S|Ph\.?D)[\s\S]{1,50}?(20\d{2}[\s\S]{1,20}?20\d{2}|present)",
    r"(University|Institute|College)[\s\S]{1,30}?(20\d{2}[\s\S]{1,20}?20\d{2}|present)",
]

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file with error handling"""
    try:
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file with error handling"""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise

def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_patterns = [
        r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b',
        r'\b\(\d{3}\)\s*\d{3}[-.\s]??\d{4}\b',
        r'\b\d{10}\b'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_cgpa(text: str) -> Optional[float]:
    """Extract CGPA from text with multiple patterns"""
    cgpa_patterns = [
        r'CGPA\s*[:]?\s*(\d\.\d{1,2})',
        r'(\d\.\d{1,2})\s*CGPA',
        r'GPA\s*[:]?\s*(\d\.\d{1,2})',
        r'(\d\.\d{1,2})\s*GPA',
        r'Grade\s*[:]?\s*(\d\.\d{1,2})'
    ]
    
    for pattern in cgpa_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None

def extract_skills(text: str) -> Dict[str, List[str]]:
    """Extract skills from text categorized by type"""
    found_skills = {category: [] for category in SKILLS_DB.keys()}
    
    for category, skills in SKILLS_DB.items():
        for skill in skills:
            # Use word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills[category].append(skill)
    
    return found_skills

def extract_branch(text: str) -> Optional[str]:
    """Extract branch from text"""
    branch_patterns = {
        "CSE": [r"Computer Science", r"C\.S\.E", r"CSE", r"Computer Engineering"],
        "ECE": [r"Electronics", r"E\.C\.E", r"ECE", r"Electronics and Communication"],
        "IT": [r"Information Technology", r"I\.T", r"IT"],
        "ME": [r"Mechanical", r"M\.E", r"ME", r"Mechanical Engineering"],
        "CE": [r"Civil", r"C\.E", r"CE", r"Civil Engineering"],
        "EEE": [r"Electrical", r"E\.E\.E", r"EEE", r"Electrical Engineering"]
    }
    
    for branch, patterns in branch_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return branch
    return None

def extract_experience(text: str) -> Tuple[Optional[float], List[str]]:
    """Extract total experience and companies worked at"""
    # Experience patterns
    experience_pattern = r'(\d+[\+\s]*(?:years|yrs|yr))'
    match = re.search(experience_pattern, text, re.IGNORECASE)
    experience = float(match.group(1).split()[0]) if match else None
    
    # Company patterns (simplified)
    company_pattern = r'(?:at|in|from)\s+([A-Z][a-zA-Z\s\.&]+?)(?=\s|\,|\.)'
    companies = re.findall(company_pattern, text, re.IGNORECASE)
    
    return experience, companies

def extract_education(text: str) -> List[Dict]:
    """Extract education details"""
    education_details = []
    
    for pattern in EDUCATION_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            education_details.append({
                "degree": match.group(0),
                "text": match.group(0)
            })
    
    return education_details

def parse_resume(file_path: str) -> Dict:
    """Main function to parse resume and extract all relevant information"""
    try:
        text = ""
        
        # File type detection and text extraction
        if file_path.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Resume appears to be empty or too short")
        
        # Extract all information
        cgpa = extract_cgpa(text)
        skills = extract_skills(text)
        branch = extract_branch(text)
        email = extract_email(text)
        phone = extract_phone(text)
        experience, companies = extract_experience(text)
        education = extract_education(text)
        
        # Calculate a completeness score
        completeness_score = 0
        if cgpa: completeness_score += 15
        if skills: completeness_score += 25
        if branch: completeness_score += 10
        if email: completeness_score += 10
        if phone: completeness_score += 10
        if experience is not None: completeness_score += 15
        if education: completeness_score += 15
        
        return {
            "cgpa": cgpa,
            "skills": skills,
            "branch": branch,
            "contact": {
                "email": email,
                "phone": phone
            },
            "experience": {
                "total_years": experience,
                "companies": companies
            },
            "education": education,
            "completeness_score": completeness_score,
            "raw_text": text[:1000] + "..." if len(text) > 1000 else text
        }
        
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        return {
            "error": str(e),
            "completeness_score": 0
        }
