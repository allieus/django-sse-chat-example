from django.http import HttpResponse
from django.shortcuts import render

from chat.forms import MessageForm


def index(request):
    return render(request, "chat/index.html")


# GET 요청
def chat_messages(request):
    # channel layer 구현 + SSE를 통해 수신된 다른 이의 채팅 메시지를 클라이언트로 내려줌.
    pass


# POST 요청
def chat_message_new(request):
    form = MessageForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        text = form.cleaned_data
        # TODO: channel layer를 통해서 다른 유저에게 전파
        username = request.user.username or "anonymous"
        return HttpResponse(f"""
            <p><strong class="mr-1">{username}</strong>{text}</p>
        """)
    else:
        return HttpResponse(f"""
            <p class="text-red-500">{form.errors}</p>
        """)
