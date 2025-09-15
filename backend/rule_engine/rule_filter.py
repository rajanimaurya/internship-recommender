import logging
import re
from typing import Dict, List, Tuple, Any
from utils.resume_parser import parse_resume

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self):
        self.rules = []
        # Updated weights to include rural location, category and attempt
        self.weights = {
            "cgpa": 0.15,           # Reduced from 0.25
            "skills": 0.25,         # Reduced from 0.35
            "experience": 0.10,     # Reduced from 0.20
            "education": 0.08,      # Reduced from 0.10
            "completeness": 0.07,   # Reduced from 0.10
            "rural_location": 0.15, # NEW: Rural location weight
            "category": 0.12,       # NEW: Category weight
            "attempt": 0.08         # NEW: Attempt number weight
        }
    
    def add_rule(self, rule_func, weight=1.0):
        """Add a custom rule to the engine"""
        self.rules.append({"func": rule_func, "weight": weight})
    
    def extract_all_skills(self, resume_data: Dict) -> List[str]:
        """Extract all skills from resume data"""
        all_skills = []
        for category in resume_data.get("skills", {}).values():
            all_skills.extend(category)
        return all_skills
    
    def calculate_skill_match(self, required_skills: List[str], resume_skills: List[str]) -> Tuple[float, List[str]]:
        """Calculate skill match ratio and found skills"""
        if not required_skills:
            return 1.0, []
        
        found_skills = []
        for req_skill in required_skills:
            # Case insensitive and partial matching
            for resume_skill in resume_skills:
                if req_skill.lower() in resume_skill.lower() or resume_skill.lower() in req_skill.lower():
                    found_skills.append(req_skill)
                    break
        
        skill_match_ratio = len(found_skills) / len(required_skills)
        return skill_match_ratio, found_skills
    
    def check_aap_factors(self, resume_data: Dict) -> Dict:
        """
        Check AAP specific factors: rural location, category, and attempt
        Returns scores for each factor
        """
        # Default values
        rural_score = 0.0
        category_score = 0.5  # Default medium score
        attempt_score = 1.0   # Default highest score for first attempt
        
        # Extract AAP-specific data (you'll need to modify your resume parser to extract these)
        location = resume_data.get("location", "").lower()
        category = resume_data.get("category", "").lower()
        attempt = resume_data.get("attempt", 1)  # Default to first attempt
        
        # Rural Location Scoring (1.0 for rural, 0.7 for semi-urban, 0.4 for urban)
        rural_keywords = ["village", "gramin", "gaon", "rural", "block", "tehsil"]
        urban_keywords = ["city", "metro", "urban", "municipal"]
        
        if any(keyword in location for keyword in rural_keywords):
            rural_score = 1.0
        elif any(keyword in location for keyword in urban_keywords):
            rural_score = 0.4
        else:
            rural_score = 0.7  # Semi-urban
        
        # Category Scoring (Higher for marginalized categories)
        if "sc" in category or "st" in category:
            category_score = 1.0
        elif "obc" in category:
            category_score = 0.8
        elif "general" in category or "unreserved" in category:
            category_score = 0.6
        else:
            category_score = 0.5  # Unknown category
        
        # Attempt Scoring (Higher for fewer attempts)
        if attempt == 1:
            attempt_score = 1.0
        elif attempt == 2:
            attempt_score = 0.7
        elif attempt == 3:
            attempt_score = 0.4
        else:
            attempt_score = 0.2  # More than 3 attempts
        
        return {
            "rural_location": rural_score,
            "category": category_score,
            "attempt": attempt_score
        }
    
    def check_minimum_requirements(self, resume_data: Dict, requirements: Dict) -> Tuple[bool, Dict]:
        """
        Check if resume meets minimum requirements with AAP factors
        """
        results = {
            "cgpa_check": {"passed": False, "details": "", "score": 0},
            "skills_check": {"passed": False, "details": "", "score": 0, "found_skills": [], "missing_skills": []},
            "branch_check": {"passed": False, "details": "", "score": 0},
            "experience_check": {"passed": False, "details": "", "score": 0},
            "completeness_check": {"passed": False, "details": "", "score": 0},
            "rural_location_check": {"passed": False, "details": "", "score": 0},  # NEW
            "category_check": {"passed": False, "details": "", "score": 0},       # NEW
            "attempt_check": {"passed": False, "details": "", "score": 0},        # NEW
            "total_score": 0,
            "all_checks_passed": False
        }
        
        try:
            # Check AAP factors first
            aap_scores = self.check_aap_factors(resume_data)
            
            # Rural Location Check
            rural_threshold = requirements.get("min_rural_score", 0.3)
            if aap_scores["rural_location"] >= rural_threshold:
                results["rural_location_check"]["passed"] = True
                results["rural_location_check"]["details"] = f"Rural location score: {aap_scores['rural_location']}"
            else:
                results["rural_location_check"]["details"] = f"Rural location score too low: {aap_scores['rural_location']}"
            results["rural_location_check"]["score"] = self.weights["rural_location"] * aap_scores["rural_location"]
            
            # Category Check
            category_threshold = requirements.get("min_category_score", 0.4)
            if aap_scores["category"] >= category_threshold:
                results["category_check"]["passed"] = True
                results["category_check"]["details"] = f"Category score: {aap_scores['category']}"
            else:
                results["category_check"]["details"] = f"Category score too low: {aap_scores['category']}"
            results["category_check"]["score"] = self.weights["category"] * aap_scores["category"]
            
            # Attempt Check
            attempt_threshold = requirements.get("min_attempt_score", 0.3)
            if aap_scores["attempt"] >= attempt_threshold:
                results["attempt_check"]["passed"] = True
                results["attempt_check"]["details"] = f"Attempt score: {aap_scores['attempt']}"
            else:
                results["attempt_check"]["details"] = f"Attempt score too low: {aap_scores['attempt']}"
            results["attempt_check"]["score"] = self.weights["attempt"] * aap_scores["attempt"]
            
            # Original checks (CGPA, Skills, etc.) - with reduced weights
            # CGPA Check
            min_cgpa = float(requirements.get("min_cgpa", 0))
            resume_cgpa = resume_data.get("cgpa")
            
            if resume_cgpa is not None:
                resume_cgpa = float(resume_cgpa)
                if resume_cgpa >= min_cgpa:
                    results["cgpa_check"]["passed"] = True
                    results["cgpa_check"]["details"] = f"CGPA {resume_cgpa} >= {min_cgpa}"
                    results["cgpa_check"]["score"] = self.weights["cgpa"]
                else:
                    results["cgpa_check"]["details"] = f"CGPA {resume_cgpa} < {min_cgpa}"
                    if min_cgpa > 0:
                        cgpa_ratio = resume_cgpa / min_cgpa
                        results["cgpa_check"]["score"] = self.weights["cgpa"] * min(cgpa_ratio, 1.0)
            else:
                results["cgpa_check"]["details"] = "CGPA not found in resume"
            
            # Skills Check
            required_skills = requirements.get("required_skills", [])
            all_skills = self.extract_all_skills(resume_data)
            
            if required_skills:
                skill_match_ratio, found_skills = self.calculate_skill_match(required_skills, all_skills)
                missing_skills = [skill for skill in required_skills if skill not in found_skills]
                
                min_skill_match = requirements.get("min_skill_match", 0.5)
                if skill_match_ratio >= min_skill_match:
                    results["skills_check"]["passed"] = True
                    results["skills_check"]["details"] = f"Found {len(found_skills)}/{len(required_skills)} required skills"
                else:
                    results["skills_check"]["details"] = f"Found only {len(found_skills)}/{len(required_skills)} required skills"
                
                results["skills_check"]["found_skills"] = found_skills
                results["skills_check"]["missing_skills"] = missing_skills
                results["skills_check"]["score"] = self.weights["skills"] * skill_match_ratio
            else:
                results["skills_check"]["passed"] = True
                results["skills_check"]["details"] = "No skills required"
                results["skills_check"]["score"] = self.weights["skills"]
            
            # Branch Check
            required_branch = requirements.get("required_branch", "").upper()
            resume_branch = resume_data.get("branch", "").upper() if resume_data.get("branch") else ""
            
            if required_branch:
                if resume_branch and resume_branch == required_branch:
                    results["branch_check"]["passed"] = True
                    results["branch_check"]["details"] = f"Branch {resume_branch} matches required {required_branch}"
                    results["branch_check"]["score"] = self.weights["education"]
                else:
                    results["branch_check"]["details"] = f"Branch {resume_branch if resume_branch else 'not found'} doesn't match required {required_branch}"
            else:
                results["branch_check"]["passed"] = True
                results["branch_check"]["details"] = "No branch requirement"
                results["branch_check"]["score"] = self.weights["education"]
            
            # Experience Check
            min_experience = float(requirements.get("min_experience", 0))
            experience = float(resume_data.get("experience", {}).get("total_years", 0) or 0)
            
            if experience >= min_experience:
                results["experience_check"]["passed"] = True
                results["experience_check"]["details"] = f"Experience {experience} years >= {min_experience} years"
                results["experience_check"]["score"] = self.weights["experience"]
            else:
                results["experience_check"]["details"] = f"Experience {experience} years < {min_experience} years"
                if min_experience > 0:
                    exp_ratio = experience / min_experience
                    results["experience_check"]["score"] = self.weights["experience"] * min(exp_ratio, 1.0)
            
            # Completeness Check
            min_completeness = float(requirements.get("min_completeness", 50))
            completeness = float(resume_data.get("completeness_score", 0))
            
            if completeness >= min_completeness:
                results["completeness_check"]["passed"] = True
                results["completeness_check"]["details"] = f"Completeness score {completeness} >= {min_completeness}"
                results["completeness_check"]["score"] = self.weights["completeness"]
            else:
                results["completeness_check"]["details"] = f"Completeness score {completeness} < {min_completeness}"
                if min_completeness > 0:
                    comp_ratio = completeness / min_completeness
                    results["completeness_check"]["score"] = self.weights["completeness"] * min(comp_ratio, 1.0)
            
            # Calculate overall score with AAP factors
            total_score = (
                results["cgpa_check"]["score"] +
                results["skills_check"]["score"] +
                results["branch_check"]["score"] +
                results["experience_check"]["score"] +
                results["completeness_check"]["score"] +
                results["rural_location_check"]["score"] +
                results["category_check"]["score"] +
                results["attempt_check"]["score"]
            )
            
            results["total_score"] = round(total_score * 100, 2)
            
            # Check if all requirements are met
            min_score = float(requirements.get("min_score", 70))
            results["all_checks_passed"] = results["total_score"] >= min_score
            
            return results["all_checks_passed"], results
            
        except Exception as e:
            logger.error(f"Error in requirement checking: {e}")
            return False, {"total_score": 0, "all_checks_passed": False, "error": str(e)}
    
    def filter_resume(self, file_path: str, requirements: Dict) -> Tuple[bool, Dict]:
        """
        Complete resume filtering process with AAP factors
        """
        try:
            # Parse resume
            resume_data = parse_resume(file_path)
            
            if "error" in resume_data:
                return False, {"error": resume_data["error"]}
            
            # Check requirements
            passes, check_results = self.check_minimum_requirements(resume_data, requirements)
            
            return passes, {
                "resume_data": resume_data,
                "check_results": check_results
            }
            
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            return False, {"error": str(e)}
    
    def get_detailed_analysis(self, resume_data: Dict, requirements: Dict) -> Dict:
        """
        Get detailed analysis for recommendation explanation with AAP factors
        """
        passes, results = self.check_minimum_requirements(resume_data, requirements)
        
        analysis = {
            "passes": passes,
            "total_score": results["total_score"],
            "breakdown": {
                "cgpa": {
                    "score": results["cgpa_check"]["score"] * 100,
                    "details": results["cgpa_check"]["details"],
                    "passed": results["cgpa_check"]["passed"]
                },
                "skills": {
                    "score": results["skills_check"]["score"] * 100,
                    "details": results["skills_check"]["details"],
                    "found_skills": results["skills_check"]["found_skills"],
                    "missing_skills": results["skills_check"]["missing_skills"],
                    "passed": results["skills_check"]["passed"]
                },
                "branch": {
                    "score": results["branch_check"]["score"] * 100,
                    "details": results["branch_check"]["details"],
                    "passed": results["branch_check"]["passed"]
                },
                "experience": {
                    "score": results["experience_check"]["score"] * 100,
                    "details": results["experience_check"]["details"],
                    "passed": results["experience_check"]["passed"]
                },
                "completeness": {
                    "score": results["completeness_check"]["score"] * 100,
                    "details": results["completeness_check"]["details"],
                    "passed": results["completeness_check"]["passed"]
                },
                "rural_location": {
                    "score": results["rural_location_check"]["score"] * 100,
                    "details": results["rural_location_check"]["details"],
                    "passed": results["rural_location_check"]["passed"]
                },
                "category": {
                    "score": results["category_check"]["score"] * 100,
                    "details": results["category_check"]["details"],
                    "passed": results["category_check"]["passed"]
                },
                "attempt": {
                    "score": results["attempt_check"]["score"] * 100,
                    "details": results["attempt_check"]["details"],
                    "passed": results["attempt_check"]["passed"]
                }
            }
        }
        
        return analysis

# Create a default rule engine instance
default_rule_engine = RuleEngine()
