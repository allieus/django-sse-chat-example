import asyncio
import functools
from typing import Dict

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.asyncio import aclosing
from django.views import View

from chat.forms import MessageForm


def index(request):
    return render(request, "chat/index.html")



class ChatSSEView(View):
    group_name = f"lobby"  # TODO: 동적으로 결정
    channel_layer_alias = "default"
    # message_template_name = "chat/_message.html"

    def get_group_name(self) -> str:
        return self.group_name

    def get_channel_layer_alias(self) -> str:
        return self.channel_layer_alias

    async def get(self, request):
        async def stream():
            # channel layer 구현 + SSE를 통해 수신된 다른 이의 채팅 메시지를 클라이언트로 내려줌.

            channel_layer = get_channel_layer(self.get_channel_layer_alias())
            if channel_layer is None:
                # render_to_string
                yield "data: <p>channel_layer default 설정을 해주세요.</p>>\n\n"
            else:
                channel_name = await channel_layer.new_channel()
                channel_receive = functools.partial(channel_layer.receive, channel_name)

                try:
                    await channel_layer.group_add(self.get_group_name(), channel_name)

                    while True:
                        try:
                            new_message: Dict = await asyncio.wait_for(channel_receive(), timeout=0.5)
                            yield f"data: <p>{new_message}</p>\n\n"  # SSE
                        except asyncio.TimeoutError:
                            # TODO: keepalive
                            pass
                finally:
                    await channel_layer.group_discard(self.get_group_name(), channel_name)

        async def wrapped_stream():
            # context manager
            async with aclosing(stream()) as _stream:
                async for item in _stream:
                    yield item

        response = StreamingHttpResponse(wrapped_stream(), content_type="text/event-stream")
        response["cache-control"] = "no-cache"
        return response

    async def post(self, request):
        form = MessageForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            text = form.cleaned_data["text"]

            # channel layer를 통해서 다른 유저에게 전파
            username = request.user.username or "anonymous"

            channel_layer = get_channel_layer(self.get_channel_layer_alias())
            if channel_layer is None:
                return HttpResponse("<p>channel_layer default 설정을 해주세요.</p>")
            else:
                await channel_layer.group_send(
                    self.get_group_name(),
                    {"type": "chat.message", "username": username, "text": text}
                )
                return HttpResponse()

            # return HttpResponse(f"""
            #     <p><strong class="mr-1">{username}</strong>{text}</p>
            # """)
        else:
            return HttpResponse(f"""
                <p class="text-red-500">{form.errors}</p>
            """)


chat_sse = ChatSSEView.as_view()


# class MyChatSSEView(ChatSSEView):
#     pass
