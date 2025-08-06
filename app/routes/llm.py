import os
import json
import time
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from groq import Groq

bp = Blueprint('llm', __name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
print(f"DEBUG (llm.py): OPENAI_API_KEY is {OPENAI_API_KEY}")


def call_groq_api(prompt):
    if not OPENAI_API_KEY:
        current_app.logger.error("OPENAI_API_KEY is not set.")
        raise RuntimeError("OPENAI_API_KEY not set")

    try:
        client = Groq(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2048,
            top_p=1,
            stream=False,
        )
        
        content = completion.choices[0].message.content
        current_app.logger.info(f"LLM response: {content}")
        return content

    except Exception as e:
        current_app.logger.error(f"Groq API request failed: {e}")
        raise RuntimeError(f"Failed to get response from Groq: {e}")


@bp.route("/parse-resume", methods=["POST"])
@jwt_required()
def parse_resume_llm():
    data = request.get_json() or {}
    text = data.get("resume_text", "").strip()

    if not text:
        return jsonify({"error": "No resume_text provided"}), 400

    prompt = (
        "Extract name, email, phone, education, experience, and skills from the following resume "
        "and return ONLY a valid JSON object with keys: name, email, phone, education, experience, skills. "
        "Do not include any markdown formatting, explanations, or additional text. Return only the JSON object.\n\n"
        f"Resume:\n{text}"
    )

    llm_output = None
    try:
        llm_output = call_groq_api(prompt)

        try:
            parsed = json.loads(llm_output)
        except json.JSONDecodeError:
            # Try to extract JSON from the response if it contains markdown
            import re
            # First try to find JSON in markdown blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # If that didn't work, try to find any JSON object in the response
            if 'parsed' not in locals():
                json_match = re.search(r'\{[^{}]*"name"[^{}]*\}', llm_output)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass
            
            # If still no success, return error
            if 'parsed' not in locals():
                current_app.logger.error(f"Invalid JSON from LLM: {llm_output}")
                return jsonify({
                    "error": "Invalid JSON returned by LLM",
                    "raw_response": llm_output
                }), 500

        return jsonify({"parsed": parsed}), 200

    except Exception as e:
        current_app.logger.error(f"LLM Error: {e}")
        resp = {"error": str(e)}
        if llm_output:
            resp["raw_response"] = llm_output
        return jsonify(resp), 500


@bp.route("/match-jobs", methods=["POST"])
@jwt_required()
def match_jobs():
    """Match parsed resume with available job profiles."""
    data = request.get_json() or {}
    parsed_resume = data.get("parsed_resume")
    
    if not parsed_resume:
        return jsonify({"error": "No parsed resume provided"}), 400
    
    try:
        # Get available jobs from database
        from ..models.job import Job
        result = Job.get_all(status=None, page=1, per_page=1000)  # Get all jobs
        jobs = result['jobs']
        
        if not jobs:
            return jsonify({"error": "No jobs available for matching"}), 404
        
        # Create a prompt for job matching
        resume_text = f"""
        Name: {parsed_resume.get('name', 'N/A')}
        Email: {parsed_resume.get('email', 'N/A')}
        Phone: {parsed_resume.get('phone', 'N/A')}
        Education: {parsed_resume.get('education', 'N/A')}
        Experience: {parsed_resume.get('experience', 'N/A')}
        Skills: {parsed_resume.get('skills', 'N/A')}
        """
        
        job_descriptions = []
        for job in jobs:
            job_desc = f"""
            Job Title: {job.title}
            Description: {job.description}
            Requirements: {job.requirements}
            """
            job_descriptions.append({
                "id": job.id,
                "title": job.title,
                "description": job_desc
            })
        
        # Create matching prompt
        matching_prompt = f"""
        Given the following candidate resume:
        {resume_text}
        
        And these available job positions:
        {chr(10).join([f"{i+1}. {job['title']}: {job['description']}" for i, job in enumerate(job_descriptions)])}
        
        Please analyze the candidate's fit for each job and return a JSON response with:
        1. Overall match scores (0-10) for each job
        2. Detailed reasoning for each match
        3. Top 3 recommended jobs
        
        Return the response as a JSON object with this structure:
        {{
            "matches": [
                {{
                    "job_id": <job_id>,
                    "job_title": "<job_title>",
                    "match_score": <score_0_10>,
                    "reasoning": "<detailed_reasoning>"
                }}
            ],
            "top_recommendations": [
                {{
                    "job_id": <job_id>,
                    "job_title": "<job_title>",
                    "match_score": <score_0_10>
                }}
            ]
        }}
        """
        
        # Call LLM for job matching
        llm_output = call_groq_api(matching_prompt)
        
        try:
            matches = json.loads(llm_output)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
            if json_match:
                try:
                    matches = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    current_app.logger.error(f"Invalid JSON from job matching LLM: {llm_output}")
                    return jsonify({
                        "error": "Invalid JSON returned by LLM for job matching",
                        "raw_response": llm_output
                    }), 500
            else:
                current_app.logger.error(f"Invalid JSON from job matching LLM: {llm_output}")
                return jsonify({
                    "error": "Invalid JSON returned by LLM for job matching",
                    "raw_response": llm_output
                }), 500
        
        return jsonify({
            "matches": matches.get("matches", []),
            "top_recommendations": matches.get("top_recommendations", []),
            "resume": parsed_resume
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Job matching error: {e}")
        return jsonify({"error": f"Job matching failed: {str(e)}"}), 500


@bp.route("/rank-candidate", methods=["POST"])
@jwt_required()
def rank_candidate_llm():
    data = request.get_json() or {}
    resume_info = data.get("resume")
    job_desc = data.get("job")

    if not resume_info or not job_desc:
        return jsonify({"error": "Both resume and job required"}), 400

    raw_text = resume_info.get("raw_text", "")
    sections = raw_text.split("\n\n")
    trimmed_sections = [
        sec for sec in sections
        if sec.strip().lower().startswith("skills") or sec.strip().lower().startswith("experience")
    ]
    trimmed_text = "\n\n".join(trimmed_sections)

    prompt = (
        f"Job description:\n{job_desc}\n\n"
        f"Candidate Skills & Experience:\n{trimmed_text}\n\n"
        "Rate the fit of this candidate for the job on a scale of 0–10 and return a JSON object "
        "in this format: {\"score\": <number>, \"rationale\": <string>}."
    )

    llm_output = None
    try:
        llm_output = call_groq_api(prompt)

        try:
            result = json.loads(llm_output)
        except json.JSONDecodeError:
            # Try to extract JSON from the response if it contains markdown
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    current_app.logger.error(f"Invalid JSON from LLM: {llm_output}")
                    return jsonify({
                        "error": "Invalid JSON returned by LLM",
                        "raw_response": llm_output
                    }), 500
            else:
                current_app.logger.error(f"Invalid JSON from LLM: {llm_output}")
                return jsonify({
                    "error": "Invalid JSON returned by LLM",
                    "raw_response": llm_output
                }), 500

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"LLM Error: {e}")
        resp = {"error": str(e)}
        if llm_output:
            resp["raw_response"] = llm_output
        return jsonify(resp), 500
