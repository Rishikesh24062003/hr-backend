import os
from app import create_app

app = create_app()

# For Vercel deployment
if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
