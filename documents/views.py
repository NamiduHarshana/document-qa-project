import time
from rest_framework import viewsets
from .models import Document
from .serializers import DocumentSerializer
import pdfplumber
from docx import Document as DocxReader
from google import genai
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


def get_session_id(request):
    """Get session_id from request header, sent by frontend."""
    return request.headers.get('X-Session-Id', 'anonymous')


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        session_id = get_session_id(self.request)
        return Document.objects.filter(session_id=session_id).order_by('-uploaded_at')

    def perform_create(self, serializer):
        session_id = get_session_id(self.request)
        document = serializer.save(session_id=session_id)
        extracted_text = self.extract_text(document)
        document.extracted_text = extracted_text
        document.save()

    def extract_text(self, document):
        file_path = document.file.path
        text = ""

        try:
            if file_path.endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

            elif file_path.endswith('.docx'):
                doc = DocxReader(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"

        except Exception as e:
            text = f"Error extracting text: {str(e)}"

        return text


@api_view(['POST'])
def chat_with_documents(request):
    question = request.data.get('question', '')
    document_id = request.data.get('document_id')
    session_id = get_session_id(request)

    if not question:
        return Response({'error': 'Question is required'}, status=400)

    documents_qs = Document.objects.filter(session_id=session_id).exclude(extracted_text='')

    if document_id:
        documents_qs = documents_qs.filter(id=document_id)

    context = ""
    for doc in documents_qs:
        context += f"\n\n--- Document: {doc.title} ---\n{doc.extracted_text}"

    if not context:
        return Response({'answer': 'No documents found. Please upload a document first.'})

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""You are a helpful assistant that answers questions based only on the provided documents.
If the answer is not in the documents, say "I don't have information about that in the uploaded documents."

Documents:
{context}

Question: {question}

Answer:"""

    models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-flash-latest']

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return Response({'answer': response.text})
        except Exception as e:
            if '503' in str(e) or 'UNAVAILABLE' in str(e):
                continue
            return Response({'error': str(e)}, status=500)

    return Response(
        {'answer': 'The AI service is temporarily busy. Please try again in a moment.'},
        status=200
    )