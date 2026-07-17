
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/(?P<topic>\w+)/?$", consumers.SupplyChainConsumer.as_asgi()),
]
