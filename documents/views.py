from rest_framework import viewsets
from .models import Document
from .serializers import DocumentSerializer
import pdfplumber
from docx import Document as DocxReader


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
