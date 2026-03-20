def compute_metrics(extracted, expected):
    """
    Compare extracted skills against ground truth
    Returns precision, recall, F1, and match score
    """
    ext_skills = set(s.lower().strip() for s in extracted.get("skills", []) if s)
    exp_skills = set(s.lower().strip() for s in expected.get("skills", []) if s)
    
    if not ext_skills and not exp_skills:
        return {"accuracy": 100.0, "match_score": 100.0, "precision": 100.0, "recall": 100.0}
    
    intersection = ext_skills & exp_skills
    
    precision = len(intersection) / len(ext_skills) * 100 if ext_skills else 0
    recall = len(intersection) / len(exp_skills) * 100 if exp_skills else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # Experience matching (if applicable)
    exp_match = 100.0
    if "experience_years" in expected and "experience_years" in extracted:
        diff = abs(extracted["experience_years"] - expected["experience_years"])
        exp_match = max(0, 100 - (diff * 20))  # -20% per year difference
    
    # Weighted final accuracy
    accuracy = (f1 * 0.8) + (exp_match * 0.2)
    
    return {
        "accuracy": round(accuracy, 2),
        "match_score": round(recall, 2),  # Recall = % of expected skills found
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1, 2),
        "skills_found": len(intersection),
        "skills_expected": len(exp_skills),
        "skills_extracted": len(ext_skills)
    }   