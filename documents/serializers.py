import filetype
from django.conf import settings
from rest_framework import serializers

from .models import Document

# Maps the allowed extensions to the MIME type real content must sniff as.
ALLOWED_DOCUMENT_MIME_TYPES = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'extracted_text']

    def validate_file(self, value):
        if value.size > settings.MAX_DOCUMENT_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File is too large. Max size is {settings.MAX_DOCUMENT_UPLOAD_SIZE // (1024 * 1024)}MB."
            )

        header = value.read(261)
        value.seek(0)

        kind = filetype.guess(header)
        if kind is None or kind.mime not in ALLOWED_DOCUMENT_MIME_TYPES.values():
            raise serializers.ValidationError(
                "File content does not match an allowed document type (PDF or DOCX)."
            )

        return value
