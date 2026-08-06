from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from google import genai
from .models import ChatThread, Message

client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def get_ai_reply(thread):
    history_text = "\n".join([f"{m.role}: {m.content}" for m in thread.messages.all()])
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=history_text
    )
    return response.text


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def home(request):
    threads = ChatThread.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {'threads': threads})


@login_required
def start_chat(request):
    if request.method == 'POST':
        user_text = request.POST.get('message')
        if user_text:
            thread = ChatThread.objects.create(user=request.user, title=user_text[:50])
            Message.objects.create(thread=thread, role='user', content=user_text)
            ai_reply = get_ai_reply(thread)
            Message.objects.create(thread=thread, role='assistant', content=ai_reply)
            return redirect('thread_view', thread_id=thread.id)
    return redirect('home')


@login_required
def new_thread(request):
    thread = ChatThread.objects.create(user=request.user)
    return redirect('thread_view', thread_id=thread.id)


@login_required
def thread_view(request, thread_id):
    thread = get_object_or_404(ChatThread, id=thread_id, user=request.user)
    threads = ChatThread.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        user_text = request.POST.get('message')
        Message.objects.create(thread=thread, role='user', content=user_text)
        ai_reply = get_ai_reply(thread)
        Message.objects.create(thread=thread, role='assistant', content=ai_reply)
        if thread.title == "New Chat":
            thread.title = user_text[:50]
            thread.save()
        return redirect('thread_view', thread_id=thread.id)

    messages = thread.messages.all()
    return render(request, 'thread.html', {'thread': thread, 'messages': messages, 'threads': threads})


@login_required
def delete_thread(request, thread_id):
    thread = get_object_or_404(ChatThread, id=thread_id, user=request.user)
    thread.delete()
    return redirect('home')
