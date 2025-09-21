# evaluator.py
import re

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

def compute_relevance(jd_text: str, resume_text: str, jd_skills: list):
    jd_text = clean_text(jd_text)
    resume_text = clean_text(resume_text)

    matches, missing = [], []
    score = 0

    for skill in jd_skills:
        if skill.lower() in resume_text:
            matches.append(skill)
            score += 5
        else:
            missing.append(skill)

    final_score = min(100, score)
    verdict = "High" if final_score > 70 else "Medium" if final_score > 40 else "Low"
    feedback = f"Matched: {', '.join(matches) if matches else 'None'} | Missing: {', '.join(missing) if missing else 'None'}"

    return {
        "final_score": final_score,
        "verdict": verdict,
        "missing": missing,
        "feedback": feedback
    }
