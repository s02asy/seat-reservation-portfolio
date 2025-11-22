import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL에서 performance_id 가져오기
        self.performance_id = self.scope["url_route"]["kwargs"]["performance_id"]
        self.group_name = f"performance_{self.performance_id}"

        # 그룹에 채널 등록
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 채널 제거
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # views.py 에서 group_send 할 때 type="seat_status" 로 보낼 거라 이 메서드 이름이 seat_status 이어야 함
    async def seat_status(self, event):
        # event = {"type": "seat_status", "seat_id": ..., "status": ..., "expires_at": ...}
        await self.send(text_data=json.dumps({
            "seat_id": event["seat_id"],
            "status": event["status"],
            "expires_at": event.get("expires_at"),
        }))
