from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# 1. Embedding model for similarity
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2. Small LLM for explanation
explanation_model = pipeline("text2text-generation", model="google/flan-t5-small")


def compute_similarity(resume_text: str, job_desc: str) -> dict:


    # Embedding similarity
    resume_emb = embedding_model.encode(resume_text, convert_to_tensor=True)
    jd_emb = embedding_model.encode(job_desc, convert_to_tensor=True)

    score = util.cos_sim(resume_emb, jd_emb).item()

    # Explanation generation
    prompt = f"""
    Resume: {resume_text}
    Job Description: {job_desc}
    Similarity Score: {round(score, 2)}

    Explain in simple words why this resume is a good or bad match for the job.
    """
    explanation = explanation_model(prompt, max_length=100, do_sample=True)[0]["generated_text"]

    return {
        "similarity_score": round(score, 3),
        "explanation": explanation
    }
