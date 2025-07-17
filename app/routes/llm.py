import os
import json
import requests
import time
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

bp = Blueprint('llm', __name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
print(f"DEBUG (llm.py): OPENAI_API_KEY is {OPENAI_API_KEY}")


def call_openai_api(prompt):
    if not OPENAI_API_KEY:
        current_app.logger.error("OPENAI_API_KEY is not set.")
        raise RuntimeError("OPENAI_API_KEY not set")

    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    for attempt in range(3):  # Retry up to 3 times
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                json=payload,
                timeout=30
            )


            if resp.status_code == 429:  # Rate limit
                if attempt < 2:
                    retry_after = int(resp.headers.get("Retry-After", 2))
                    wait_time = retry_after * (2 ** attempt)
                    current_app.logger.warning(f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise requests.exceptions.HTTPError("Rate limit exceeded after retries", response=resp)

            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            current_app.logger.info(f"LLM response: {content}")
            return content

        except requests.exceptions.HTTPError as e:
            if attempt < 2 and e.response.status_code == 429:
                continue
            else:
                raise
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"OpenAI request failed: {e}")
            if attempt == 2:
                raise

    raise RuntimeError("Failed to get response from OpenAI after multiple retries.")


@bp.route("/parse-resume", methods=["POST"])
@jwt_required()
def parse_resume_llm():
    data = request.get_json() or {}
    text = data.get("resume_text", "").strip()

    if not text:
        return jsonify({"error": "No resume_text provided"}), 400

    prompt = (
        "Extract name, email, phone, education, experience, and skills from the following resume "
        "and return as JSON with keys: name, email, phone, education, experience, skills.\n\n"
        f"Resume:\n{text}"
    )

    llm_output = None
    try:
        llm_output = call_openai_api(prompt)

        try:
            parsed = json.loads(llm_output)
        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON from LLM: {llm_output}")
            return jsonify({
                "error": "Invalid JSON returned by LLM",
                "raw_response": llm_output
            }), 500

        return jsonify({"parsed": parsed}), 200

    except requests.exceptions.HTTPError as he:
        current_app.logger.error(f"LLM HTTP error: {he}")
        return jsonify({"error": f"LLM HTTP error: {he}"}), 500
    except Exception as e:
        current_app.logger.error(f"LLM Error: {e}")
        resp = {"error": str(e)}
        if llm_output:
            resp["raw_response"] = llm_output
        return jsonify(resp), 500


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
        llm_output = call_openai_api(prompt)

        try:
            result = json.loads(llm_output)
        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON from LLM: {llm_output}")
            return jsonify({
                "error": "Invalid JSON returned by LLM",
                "raw_response": llm_output
            }), 500

        return jsonify(result), 200

    except requests.exceptions.HTTPError as he:
        current_app.logger.error(f"LLM HTTP error: {he}")
        return jsonify({"error": f"LLM HTTP error: {he}"}), 500
    except Exception as e:
        current_app.logger.error(f"LLM Error: {e}")
        resp = {"error": str(e)}
        if llm_output:
            resp["raw_response"] = llm_output
        return jsonify(resp), 500
