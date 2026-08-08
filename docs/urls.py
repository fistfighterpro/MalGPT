from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:doc_id>/', views.document_qa, name='document_qa'),
    path('documents/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
]
