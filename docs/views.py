import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from google import genai
from pypdf import PdfReader
from .models import Document, DocumentChunk

client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    else:
        with open(file_path, 'r', errors='ignore') as f:
            return f.read()


def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def embed_text(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        doc = Document.objects.create(
            user=request.user,
            file=uploaded_file,
            filename=uploaded_file.name
        )
        text = extract_text(doc.file.path)
        chunks = chunk_text(text)
        for chunk in chunks:
            vector = embed_text(chunk)
            DocumentChunk.objects.create(document=doc, content=chunk, embedding=vector)
        return redirect('document_qa', doc_id=doc.id)

    return render(request, 'docs/list.html', {'documents': documents})


@login_required
def document_qa(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    answer = None
    question = None

    if request.method == 'POST':
        question = request.POST.get('question')
        q_vector = embed_text(question)

        chunks = list(doc.chunks.all())
        scored = [(cosine_similarity(q_vector, c.embedding), c.content) for c in chunks]
        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [content for _, content in scored[:4]]

        context = "\n---\n".join(top_chunks)
        prompt = f"Answer the question using ONLY the context below. If the answer isn't in the context, say so.\n\nContext:\n{context}\n\nQuestion: {question}"

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        answer = response.text

    return render(request, 'docs/qa.html', {'doc': doc, 'answer': answer, 'question': question})


@login_required
def delete_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    doc.delete()
    return redirect('document_list')
