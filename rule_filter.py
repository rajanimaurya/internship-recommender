import logging
from typing import Dict, List, Tuple, Any
from utils.resume_parser import parse_resume

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self):
        self.rules = []
        self.weights = {
            "cgpa": 0.25,
            "skills": 0.35,
            "experience": 0.20,
            "education": 0.10,
            "completeness": 0.10
        }
    
    def add_rule(self, rule_func, weight=1.0):
        """Add a custom rule to the engine"""
        self.rules.append({"func": rule_func, "weight": weight})
    
    def check_minimum_requirements(self, resume_data: Dict, requirements: Dict) -> Tuple[bool, Dict]:
        """
        Check if resume meets minimum requirements
        
        Parameters:
        - resume_data: Dictionary from parse_resume()
        - requirements: Dictionary of requirements
        
        Returns:
        - Boolean: True if meets requirements, False otherwise
        - Dictionary: Detailed results of each check
        """
        results = {
            "cgpa_check": {"passed": False, "details": ""},
            "skills_check": {"passed": False, "details": ""},
            "branch_check": {"passed": False, "details": ""},
            "experience_check": {"passed": False, "details": ""},
            "completeness_check": {"passed": False, "details": ""},
            "score": 0,
            "all_checks_passed": False
        }
        
        # CGPA Check
        min_cgpa = requirements.get("min_cgpa", 0)
        if resume_data.get("cgpa") is not None:
            if resume_data["cgpa"] >= min_cgpa:
                results["cgpa_check"]["passed"] = True
                results["cgpa_check"]["details"] = f"CGPA {resume_data['cgpa']} >= {min_cgpa}"
            else:
                results["cgpa_check"]["details"] = f"CGPA {resume_data['cgpa']} < {min_cgpa}"
        else:
            results["cgpa_check"]["details"] = "CGPA not found in resume"
        
        # Skills Check
        required_skills = requirements.get("required_skills", [])
        if required_skills:
            all_skills = []
            for category in resume_data.get("skills", {}).values():
                all_skills.extend(category)
            
            found_skills = [skill for skill in required_skills if skill in all_skills]
            skill_match_ratio = len(found_skills) / len(required_skills) if required_skills else 1
            
            if skill_match_ratio >= requirements.get("min_skill_match", 0.5):
                results["skills_check"]["passed"] = True
                results["skills_check"]["details"] = f"Found {len(found_skills)}/{len(required_skills)} required skills: {found_skills}"
            else:
                results["skills_check"]["details"] = f"Found only {len(found_skills)}/{len(required_skills)} required skills: {found_skills}"
        else:
            results["skills_check"]["passed"] = True
            results["skills_check"]["details"] = "No skills required"
        
        # Branch Check
        required_branch = requirements.get("required_branch")
        if required_branch:
            if resume_data.get("branch") and resume_data["branch"].upper() == required_branch.upper():
                results["branch_check"]["passed"] = True
                results["branch_check"]["details"] = f"Branch {resume_data['branch']} matches required {required_branch}"
            else:
                results["branch_check"]["details"] = f"Branch {resume_data.get('branch', 'not found')} doesn't match required {required_branch}"
        else:
            results["branch_check"]["passed"] = True
            results["branch_check"]["details"] = "No branch requirement"
        
        # Experience Check
        min_experience = requirements.get("min_experience", 0)
        experience = resume_data.get("experience", {}).get("total_years", 0) or 0
        if experience >= min_experience:
            results["experience_check"]["passed"] = True
            results["experience_check"]["details"] = f"Experience {experience} years >= {min_experience} years"
        else:
            results["experience_check"]["details"] = f"Experience {experience} years < {min_experience} years"
        
        # Completeness Check
        min_completeness = requirements.get("min_completeness", 50)
        completeness = resume_data.get("completeness_score", 0)
        if completeness >= min_completeness:
            results["completeness_check"]["passed"] = True
            results["completeness_check"]["details"] = f"Completeness score {completeness} >= {min_completeness}"
        else:
            results["completeness_check"]["details"] = f"Completeness score {completeness} < {min_completeness}"
        
        # Calculate overall score
        score = 0
        if results["cgpa_check"]["passed"]: score += self.weights["cgpa"]
        if results["skills_check"]["passed"]: score += self.weights["skills"]
        if results["branch_check"]["passed"]: score += self.weights["education"]  # Using education weight for branch
        if results["experience_check"]["passed"]: score += self.weights["experience"]
        if results["completeness_check"]["passed"]: score += self.weights["completeness"]
        
        results["score"] = round(score * 100, 2)
        
        # Check if all requirements are met
        min_score = requirements.get("min_score", 70)
        results["all_checks_passed"] = results["score"] >= min_score
        
        return results["all_checks_passed"], results
    
    def filter_resume(self, file_path: str, requirements: Dict) -> Tuple[bool, Dict]:
        """
        Complete resume filtering process
        
        Returns:
        - Boolean: True if resume passes all filters
        - Dictionary: Parsed data and check results
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

# Create a default rule engine instance
default_rule_engine = RuleEngine()

# Example usage
if __name__ == "__main__":
    # Initialize rule engine
    rule_engine = RuleEngine()
    
    # Define job requirements
    job_requirements = {
        "min_cgpa": 7.0,
        "required_skills": ["Python", "Machine Learning", "SQL"],
        "required_branch": "CSE",
        "min_experience": 1,
        "min_completeness": 60,
        "min_score": 65
    }
    
    # Test with a sample resume
    file_path = "../static/resumes/sample_resume.pdf"
    
    passes, results = rule_engine.filter_resume(file_path, job_requirements)
    
    print(f"Resume passes: {passes}")
    print(f"Overall score: {results['check_results']['score']}%")
    print("\nDetailed results:")
    for check, result in results["check_results"].items():
        if check not in ["score", "all_checks_passed"]:
            print(f"{check}: {result}")