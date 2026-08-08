import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document


@pytest.mark.django_db
class TestDocumentAPI:

    def test_list_documents_empty(self):
        """GET /api/documents/ returns empty list when no documents exist"""
        client = APIClient()
        response = client.get('/api/documents/')
        assert response.status_code == 200
        assert response.data == []

    def test_upload_document(self):
        """POST /api/documents/ successfully creates a document"""
        client = APIClient()
        fake_file = SimpleUploadedFile(
            "test.txt", b"Hello world content", content_type="text/plain"
        )
        response = client.post('/api/documents/', {
            'title': 'Test Document',
            'file': fake_file,
        }, format='multipart')
        assert response.status_code == 201
        assert Document.objects.count() == 1
        assert Document.objects.first().title == 'Test Document'

    def test_delete_document(self):
        """DELETE /api/documents/<id>/ removes the document"""
        doc = Document.objects.create(title='To Delete', file='documents/dummy.txt')
        client = APIClient()
        response = client.delete(f'/api/documents/{doc.id}/')
        assert response.status_code == 204
        assert Document.objects.count() == 0


@pytest.mark.django_db
class TestChatAPI:

    def test_chat_without_question_returns_error(self):
        """POST /api/chat/ with no question returns 400"""
        client = APIClient()
        response = client.post('/api/chat/', {}, format='json')
        assert response.status_code == 400

    def test_chat_without_documents_returns_helpful_message(self):
        """POST /api/chat/ with no uploaded documents returns a helpful message, not an error"""
        client = APIClient()
        response = client.post('/api/chat/', {'question': 'What is this about?'}, format='json')
        assert response.status_code == 200
        assert 'No documents' in response.data['answer']
