import math
from datetime import datetime

def calculate_skill_match_score(resume_skills, job_skills):
    """Calculate skill match score between resume and job requirements."""
    if not resume_skills or not job_skills:
        return 0.0
    
    # Convert to lowercase for case-insensitive matching
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    # Calculate intersection
    matched_skills = set(resume_skills_lower) & set(job_skills_lower)
    
    if not job_skills_lower:
        return 0.0
    
    # Calculate match percentage
    match_score = len(matched_skills) / len(job_skills_lower)
    
    return min(match_score, 1.0)

def calculate_experience_score(resume_experience, job_experience_required):
    """Calculate experience score based on years of experience."""
    if not resume_experience or not job_experience_required:
        return 0.5  # Default score when experience info is not available
    
    if resume_experience >= job_experience_required:
        # Bonus for extra experience, but with diminishing returns
        excess_years = resume_experience - job_experience_required
        bonus = min(excess_years * 0.1, 0.3)  # Max 30% bonus
        return min(1.0 + bonus, 1.0)
    else:
        # Penalty for insufficient experience
        ratio = resume_experience / job_experience_required
        return max(ratio, 0.1)  # Minimum 10% score

def calculate_education_score(resume_education, job_education_required):
    """Calculate education score based on education requirements."""
    if not resume_education:
        return 0.3  # Default score for missing education info
    
    if not job_education_required:
        return 0.7  # Default score when no education requirement
    
    # Education hierarchy
    education_levels = {
        'high school': 1,
        'associate': 2,
        'bachelor': 3,
        'master': 4,
        'phd': 5,
        'doctorate': 5
    }
    
    # Extract education level from resume
    resume_level = 0
    for education in resume_education:
        education_lower = education.lower()
        for level, value in education_levels.items():
            if level in education_lower:
                resume_level = max(resume_level, value)
    
    # Extract required education level
    required_level = 0
    job_education_lower = job_education_required.lower()
    for level, value in education_levels.items():
        if level in job_education_lower:
            required_level = max(required_level, value)
    
    if resume_level >= required_level:
        return 1.0
    elif resume_level > 0:
        return resume_level / required_level
    else:
        return 0.3

def calculate_keyword_density_score(resume_text, job_description):
    """Calculate keyword density score."""
    if not resume_text or not job_description:
        return 0.0
    
    # Extract keywords from job description (simple approach)
    job_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())
    
    # Remove common words
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'a', 'an', 'this', 'that', 'these', 'those'}
    
    job_keywords = job_words - common_words
    resume_keywords = resume_words - common_words
    
    if not job_keywords:
        return 0.0
    
    # Calculate keyword match
    matched_keywords = job_keywords & resume_keywords
    keyword_score = len(matched_keywords) / len(job_keywords)
    
    return min(keyword_score, 1.0)

def calculate_overall_score(scores, weights):
    """Calculate weighted overall score."""
    if not scores or not weights:
        return 0.0
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    
    weighted_score = 0
    for component, score in scores.items():
        weight = weights.get(component, 0)
        weighted_score += score * weight
    
    return weighted_score / total_weight

def calculate_confidence_score(scores):
    """Calculate confidence score based on data availability."""
    available_scores = sum(1 for score in scores.values() if score > 0)
    total_scores = len(scores)
    
    if total_scores == 0:
        return 0.0
    
    confidence = available_scores / total_scores
    return confidence

def calculate_ranking(resume, job):
    """Calculate ranking for a resume-job pair."""
    try:
        # Extract data from resume
        resume_data = resume.parsed_data or {}
        resume_skills = resume_data.get('skills', [])
        resume_experience = resume_data.get('experience_years', 0)
        resume_education = resume_data.get('education', [])
        resume_text = resume.raw_text or ""
        
        # Extract data from job
        job_requirements = job.requirements or {}
        job_skills = job_requirements.get('skills', [])
        job_experience_required = job_requirements.get('experience_years', 0)
        job_education_required = job_requirements.get('education', "")
        job_description = job.description or ""
        
        # Calculate component scores
        scores = {
            'skills': calculate_skill_match_score(resume_skills, job_skills),
            'experience': calculate_experience_score(resume_experience, job_experience_required),
            'education': calculate_education_score(resume_education, job_education_required),
            'keywords': calculate_keyword_density_score(resume_text, job_description)
        }
        
        # Define weights for different components
        weights = {
            'skills': 0.4,      # 40% weight on skills
            'experience': 0.3,   # 30% weight on experience
            'education': 0.2,    # 20% weight on education
            'keywords': 0.1      # 10% weight on keyword density
        }
        
        # Calculate overall score
        overall_score = calculate_overall_score(scores, weights)
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(scores)
        
        # Apply confidence penalty to overall score
        final_score = overall_score * confidence_score
        
        return {
            'overall_score': min(max(final_score, 0.0), 1.0),
            'score_breakdown': scores,
            'confidence_score': confidence_score,
            'weights_used': weights,
            'calculation_timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Return default low score if calculation fails
        return {
            'overall_score': 0.1,
            'score_breakdown': {
                'skills': 0.0,
                'experience': 0.0,
                'education': 0.0,
                'keywords': 0.0
            },
            'confidence_score': 0.0,
            'error': str(e),
            'calculation_timestamp': datetime.utcnow().isoformat()
        }

def rank_resumes_for_job(resumes, job):
    """Rank multiple resumes for a single job."""
    rankings = []
    
    for resume in resumes:
        ranking_data = calculate_ranking(resume, job)
        rankings.append({
            'resume_id': resume.id,
            'resume': resume,
            'ranking_data': ranking_data
        })
    
    # Sort by overall score (descending)
    rankings.sort(key=lambda x: x['ranking_data']['overall_score'], reverse=True)
    
    return rankings

def get_ranking_insights(rankings):
    """Generate insights from ranking results."""
    if not rankings:
        return {}
    
    scores = [r['ranking_data']['overall_score'] for r in rankings]
    
    insights = {
        'total_candidates': len(rankings),
        'average_score': sum(scores) / len(scores),
        'highest_score': max(scores),
        'lowest_score': min(scores),
        'qualified_candidates': len([s for s in scores if s >= 0.7]),
        'score_distribution': {
            'excellent': len([s for s in scores if s >= 0.8]),
            'good': len([s for s in scores if 0.6 <= s < 0.8]),
            'average': len([s for s in scores if 0.4 <= s < 0.6]),
            'below_average': len([s for s in scores if 0.2 <= s < 0.4]),
            'poor': len([s for s in scores if s < 0.2])
        }
    }
    
    return insights
