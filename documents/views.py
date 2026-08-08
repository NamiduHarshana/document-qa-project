from rest_framework import viewsets
from .models import Document
from .serializers import DocumentSerializer
import pdfplumber
from docx import Document as DocxReader
from google import genai
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        document = serializer.save()
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

    if not question:
        return Response({'error': 'Question is required'}, status=400)

    all_documents = Document.objects.exclude(extracted_text='')
    context = ""
    for doc in all_documents:
        context += f"\n\n--- Document: {doc.title} ---\n{doc.extracted_text}"

    if not context:
        return Response({'answer': 'No documents have been uploaded yet. Please upload a document first.'})

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""You are a helpful assistant that answers questions based only on the provided documents.
If the answer is not in the documents, say "I don't have information about that in the uploaded documents."

Documents:
{context}

Question: {question}

Answer:"""

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        return Response({'answer': response.text})
    except Exception as e:
        return Response({'error': str(e)}, status=500)