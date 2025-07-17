import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from ..models.resume import Resume
from ..utils.resume_parser import parse_resume
from .. import db

logger = logging.getLogger(__name__)
bp = Blueprint('resumes', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET'])
@jwt_required()
def list_resumes():
    """List all uploaded resumes (paginated)."""
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    pagination = Resume.query.paginate(page=page, per_page=per_page, error_out=False)
    resumes = [r.to_dict() for r in pagination.items]
    return jsonify({
        'resumes': resumes,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload and parse a resume."""
    logger.info("upload_resume called")
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename_raw = file.filename or ""
    original = secure_filename(filename_raw)
    if not original or not allowed_file(original):
        logger.warning(f"Invalid file type: {filename_raw}")
        return jsonify({'error': 'Invalid file type'}), 400

    # Reset pointer and save
    file.stream.seek(0)
    unique_name = f"{uuid.uuid4()}_{original}"
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
    try:
        file.save(save_path)
        size = os.path.getsize(save_path)
        logger.info(f"Saved file {unique_name} ({size} bytes)")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return jsonify({'error': f"File save failed: {e}"}), 500

    # Create database record
    resume = Resume(
        filename=unique_name,
        original_filename=original,
        file_path=save_path,
        file_size=size,
        mime_type=file.content_type,
        processing_status='processing'
    )
    db.session.add(resume)
    db.session.commit()
    logger.info(f"Created resume record ID={resume.id}")

    # Parse resume text
    try:
        parsed = parse_resume(save_path)
        raw = parsed.get('raw_text', '')
        if not raw.strip():
            raise Exception("No text extracted")

        resume.raw_text = raw
        resume.parsed_data = parsed.get('structured_data', {})
        resume.candidate_name = parsed.get('name')
        resume.candidate_email = parsed.get('email')
        resume.candidate_phone = parsed.get('phone')
        resume.processing_status = 'completed'
        db.session.commit()
        logger.info(f"Resume ID={resume.id} parsed successfully")
        return jsonify({'message': 'Uploaded', 'resume': resume.to_dict(include_text=True)}), 201

    except Exception as e:
        logger.error(f"Parsing failed for resume ID={resume.id}: {e}")
        resume.processing_status = 'failed'
        resume.error_message = str(e)
        db.session.commit()
        return jsonify({'error': f"Could not extract text: {e}"}), 400

@bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id: int):
    """Retrieve a specific resume by ID."""
    resume = Resume.query.get_or_404(resume_id)
    include_text = request.args.get('include_text', 'false').lower() == 'true'
    return jsonify(resume.to_dict(include_text=include_text)), 200

@bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id: int):
    """Delete a specific resume."""
    resume = Resume.query.get_or_404(resume_id)
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
            logger.info(f"Deleted file at {resume.file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete file: {e}")
    db.session.delete(resume)
    db.session.commit()
    return jsonify({'message': 'Resume deleted successfully'}), 200
