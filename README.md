
# LinguaAI – Smart Language Translator

LinguaAI is an AI-powered language translation web application built using Python, Flask, and Large Language Models (LLMs).

It provides context-aware translations, automatic language detection, voice input, text-to-speech, translation history, and user authentication.

## Features

- AI-powered multilingual translation
- Automatic source language detection
- Context-aware translation
- Voice input using browser speech recognition
- Text-to-speech functionality
- Copy and download translated text
- Translation history using SQLite
- User registration and login
- Password hashing and session management
- Separate translation history for each user
- Translation caching for repeated requests
- OpenRouter and Groq API fallback
- API error handling and validation
- Support for 25 language options

## Technology Stack

**Frontend**
- HTML
- CSS
- JavaScript
- Browser Web Speech API

**Backend**
- Python
- Flask
- REST API

**AI and Machine Learning**
- Large Language Models
- OpenRouter API
- Groq API
- Prompt Engineering
- langdetect

**Database**
- SQLite

**Python Libraries**
- Pandas
- NumPy
- Scikit-learn
- Requests
- Joblib

## Project Structure

```text
Language-Translator/
│
├── services/
│   ├── openrouter_client.py
│   ├── translator.py
│   └── history.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── history.js
│
├── templates/
│   ├── index.html
│   ├── history.html
│   ├── login.html
│   └── register.html
│
├── .env.example
├── .gitignore
├── app.py
├── requirements.txt
├── README.md
└── test_api_errors.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Language-Translator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root.

Copy the contents of `.env.example` and add your own API keys and a randomly generated Flask secret key.

Never upload `.env` to GitHub.

### 6. Run the application

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## API Configuration

LinguaAI uses:

- OpenRouter as the primary AI provider.
- Groq as the backup AI provider.

The application attempts the primary provider first and uses the backup provider when necessary.

Valid API credentials and available provider quotas are required.

## Testing

Run the mocked API error-handling tests:

```bash
python test_api_errors.py
```

These tests cover authentication errors, rate limits, server errors, timeouts, and connection errors.

## Security

- API keys are stored in environment variables.
- Passwords are stored as secure password hashes.
- Flask sessions manage authenticated users.
- Translation history is filtered by user account.
- Database and environment files are excluded from Git.

This project is intended for educational and demonstration purposes. Additional security controls are recommended before public production deployment.

## Author

Developed as an AI-powered language translation project.

## License

This project is available for educational and learning purposes.
