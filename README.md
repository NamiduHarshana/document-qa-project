# Document Q&A Assistant — Backend

A Django REST API that powers an AI-driven document Q&A application. Users upload PDF/DOCX documents, and the system uses Retrieval-Augmented Generation (RAG) with Google's Gemini API to answer natural-language questions grounded in the uploaded content.

**Live API:** https://namidu.pythonanywhere.com/api/
**Frontend repo:** https://github.com/NamiduHarshana/document-qa-frontend
**Live app:** https://document-qa-assistant.netlify.app

---

## Features

- **Document upload & processing** — PDF and DOCX files, with automatic text extraction (pdfplumber, python-docx)
- **RAG-based AI chat** — Questions are answered using only the content of uploaded documents via the Gemini API, with a document selector to scope questions to a specific file
- **Session-based data isolation** — No login required; each browser session only sees its own documents. Documents are automatically cleared when the user closes the tab or navigates away
- **REST API** — Built with Django REST Framework (upload, list, delete, chat endpoints)
- **Automated tests** — Pytest test suite covering document and chat endpoints
- **Containerized** — Dockerfile included for portable deployment
- **CORS-configured** — Supports a decoupled frontend on a different origin

## Tech Stack

- **Framework:** Django 5.2, Django REST Framework
- **AI/LLM:** Google Gemini API (google-genai)
- **Document parsing:** pdfplumber, python-docx
- **Testing:** Pytest, pytest-django
- **Deployment:** Docker, PythonAnywhere
- **Database:** SQLite

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/documents/ | List documents for the current session |
| POST | /api/documents/ | Upload a new document |
| DELETE | /api/documents/<id>/ | Delete a document |
| POST | /api/chat/ | Ask a question (optionally scoped to one document) |
| POST | /api/documents/clear-session/ | Clear all documents for the current session |

All document/chat requests are scoped by an X-Session-Id header sent from the frontend.

## Local Setup

git clone https://github.com/NamiduHarshana/document-qa-project.git
cd document-qa-project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "GEMINI_API_KEY=your_key_here" > .env

python3 manage.py migrate
python3 manage.py runserver

## Running Tests

pytest

## Docker

docker build -t document-qa-backend .
docker run -p 8000:8000 --env-file .env document-qa-backend

## Architecture Notes

- **No traditional user accounts.** Instead of login/signup, each browser is assigned a random session ID (stored in localStorage on the frontend) which scopes all document access. This keeps the demo frictionless while still ensuring one user's documents are never visible to another.
- **RAG pipeline** is intentionally simple: extracted document text is passed directly as context to Gemini rather than using a vector database, which keeps the app lightweight and fast for typical document sizes while still grounding every answer in the source material.
