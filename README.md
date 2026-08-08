# MalGPT — AI Internship Project

A Django app combining two features: a ChatGPT-style assistant with persistent conversations, and a document upload + Q&A tool powered by retrieval-augmented generation (RAG).

## Task 1 — Chat App
- Sign up / log in / log out (Django auth)
- Create multiple chat threads per user
- Full conversation history preserved per thread
- Delete chats
- Responsive, dark-themed UI

## Task 2 — Document Q&A (RAG)
- Upload documents (PDF or text)
- Text is extracted, split into chunks, and embedded using Gemini's embedding model
- Ask questions about a document; the app retrieves the most relevant chunks (cosine similarity) and asks Gemini to answer using only that context
- Delete uploaded documents

## Tech stack
- Django 4.2
- Google Gemini API (gemini-3.6-flash for chat/answers, gemini-embedding-001 for embeddings)
- SQLite (local database)
- pypdf (PDF text extraction), numpy (similarity scoring)

## Setup

Clone the repo, then:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Create a .env file in the project root:

    GOOGLE_API_KEY=your-gemini-api-key

Then run:

    python manage.py migrate
    python manage.py runserver

Visit http://127.0.0.1:8000/

## Notes
- Uploaded documents are stored in a local media/ folder (not committed to this repo).
- The chat and document features share the same authentication and UI shell.
