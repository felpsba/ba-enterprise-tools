# BA Enterprise Tools - Web Version

This is the web version of the BA Enterprise Tools application, a translation and voiceover service.

## Local Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following content:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

## Deployment to Digital Ocean

1. Create a Digital Ocean account and set up a new App Platform project.

2. Connect your GitHub repository to Digital Ocean App Platform.

3. Configure the following settings in Digital Ocean:
   - Build Command: `docker build -t ba-enterprise-tools .`
   - Run Command: `docker run -p 8000:8000 ba-enterprise-tools`
   - Environment Variables:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `FLASK_ENV`: production
     - `FLASK_APP`: app.py

4. Deploy the application.

## Features

- User authentication
- Text translation using Google Gemini AI
- Translation history
- File upload support (PDF, DOCX)
- Dark mode interface

## Security Notes

- The application uses Flask-Login for authentication
- API keys are stored in environment variables
- All sensitive data is encrypted
- HTTPS is enforced in production

## Support

For any issues or questions, please contact the development team. 