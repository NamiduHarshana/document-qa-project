from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, chat_with_documents, clear_session_documents

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('documents/clear-session/', clear_session_documents, name='clear-session'),
] + router.urls + [
    path('chat/', chat_with_documents, name='chat'),
]