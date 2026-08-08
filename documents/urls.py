from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, chat_with_documents

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)

urlpatterns = router.urls + [
    path('chat/', chat_with_documents, name='chat'),
]