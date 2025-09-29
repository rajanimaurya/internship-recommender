import sys
import os

# Add parent directory to sys.path so imports work
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from rule_engine.rule_filter import RuleEngine
from similarity import compute_similarity
from utils.resume_parser import parse_resume

# Initialize rule engine
rule_engine = RuleEngine()


def generate_hybrid_explanation(similarity_score: float, rule_analysis: dict) -> str:
    """
    Combine rule-based analysis with similarity score into a human-readable explanation
    """
    breakdown = rule_analysis.get("breakdown", {})
    explanation_lines = []

    # Add similarity summary
    explanation_lines.append(
        f"Semantic similarity with job description: {similarity_score:.2f} (higher is better)."
    )

    # Add rule-based checks
    for criterion, details in breakdown.items():
        status = "✅ Passed" if details["passed"] else "❌ Failed"
        explanation_lines.append(f"{criterion.capitalize()}: {status} ({details['details']})")

    return "\n".join(explanation_lines)


def allocate_candidate(
    resume_path: str,
    job_desc: str,
    requirements: dict,
    industry_capacity: int = 1,
    similarity_threshold: float = 0.5
):
    """
    Process a single resume: rule filter + similarity + explanation + allocation decision
    Adds affirmative weightage for rural/aspirational districts, social categories, past attempts,
    and industry capacity.
    """
    # Step 1: Parse structured resume
    resume_data = parse_resume("C:\\Users\\govin\\sih2024\\internship-recommender\\backend\\static\\resumes\\rajni.pdf")
    if "error" in resume_data:
        return {"status": "error", "details": resume_data["error"]}

    # Step 2: Run rule-based filter
    passes, rule_results = rule_engine.check_minimum_requirements(resume_data, requirements)

    # Step 3: Compute similarity on raw text
    raw_text = resume_data.get("raw_text", "")
    similarity_results = compute_similarity(raw_text, job_desc)
    similarity_score = similarity_results["similarity_score"]

    # Step 4: Compute affirmative weightage
    aap_scores = rule_engine.check_aap_factors(resume_data)
    affirmative_score = (
        0.2 * aap_scores["rural_location"] +  # rural representation
        0.15 * aap_scores["category"] +       # social category
        0.1 * aap_scores["attempt"]           # fewer attempts get higher score
    )
    capacity_factor = 1.0 if industry_capacity > 0 else 0.0

    # Weighted final decision score
    final_score = 0.6 * similarity_score + 0.4 * (rule_results["total_score"]/100) + affirmative_score * capacity_factor

    # Step 5: Generate hybrid explanation
    hybrid_explanation = generate_hybrid_explanation(similarity_score, rule_engine.get_detailed_analysis(resume_data, requirements))
    hybrid_explanation += f"\n\nAffirmative weightage contribution: {affirmative_score:.2f} (includes rural, category, past attempts, capacity factor: {capacity_factor})"
    hybrid_explanation += f"\nFinal weighted score (similarity + rules + affirmative factors): {final_score:.2f}"

    # Step 6: Final decision
    final_decision = "Reject"
    if passes and final_score >= similarity_threshold:
        final_decision = "Allocate"

    return {
        "similarity_score": similarity_score,
        "affirmative_score": affirmative_score,
        "weighted_final_score": final_score,
        "hybrid_explanation": hybrid_explanation,
        "rule_results": rule_results,
        "system_decision": final_decision
    }


if __name__ == "__main__":
    # -----------------------------
    # Use sample resume from directory
    # -----------------------------
    sample_resume_file = os.path.join("data", "sample_resume.pdf")  # Replace with your actual sample file
    job_description = """
    Looking for an intern with Python, Flask, ML, TensorFlow, and Docker skills.
    Must have knowledge of SQL and REST APIs.
    """

    requirements = {
        "min_cgpa": 7.0,
        "required_skills": ["Python", "TensorFlow", "Docker", "SQL", "Flask"],
        "min_skill_match": 0.5,
        "min_experience": 0,
        "required_branch": "CSE",
        "min_completeness": 60,
        "min_score": 65
    }

    industry_capacity = 3  # Max interns per industry

    result = allocate_candidate(sample_resume_file, job_description, requirements, industry_capacity)

    print("\n=== Final Decision ===")
    print(f"System Decision: {result['system_decision']}")
    print(f"Similarity Score: {result['similarity_score']}")
    print(f"Affirmative Score: {result['affirmative_score']:.2f}")
    print(f"Weighted Final Score: {result['weighted_final_score']:.2f}")
    print("\n--- Explanation ---")
    print(result['hybrid_explanation'])
