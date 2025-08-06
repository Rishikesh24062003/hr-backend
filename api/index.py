from app import create_app

app = create_app()

# For Vercel serverless functions
if __name__ == "__main__":
    app.run() 