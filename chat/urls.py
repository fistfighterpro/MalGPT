from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.home, name='home'),
    path('start/', views.start_chat, name='start_chat'),
    path('thread/new/', views.new_thread, name='new_thread'),
    path('thread/<int:thread_id>/', views.thread_view, name='thread_view'),
    path('thread/<int:thread_id>/delete/', views.delete_thread, name='delete_thread'),
]
