from django.core.validators import FileExtensionValidator
from django.db import models

ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'docx']


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS)],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return self.title