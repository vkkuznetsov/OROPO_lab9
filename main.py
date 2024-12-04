import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape
import redis
import json
from tornado import gen
from config import settings

redis_client = redis.Redis(host=settings.REDIS.HOST, port=settings.REDIS.PORT, db=0)
pubsub = redis_client.pubsub()
pubsub.subscribe('chat')

clients = set()
online_users = set()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class ChatWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.id = self.get_argument("id", None)
        if not self.id:
            self.write_message(json.dumps({"type": "error", "message": "Имя пользователя не указано."}))
            self.close()
            return

        if self.id in online_users:
            self.write_message(json.dumps(
                {"type": "error", "message": "Это имя пользователя уже занято. Пожалуйста, выберите другое."}))
            self.close()
            return

        clients.add(self)
        online_users.add(self.id)

        message = {
            "type": "status",
            "message": f"Пользователь {self.id} подключился."
        }
        redis_client.publish('chat', json.dumps(message))

        self.send_current_online_users()

    def send_current_online_users(self):
        users_list = sorted(list(online_users))
        message = {
            "type": "online_users",
            "users": users_list
        }
        for client in clients:
            client.write_message(json.dumps(message))

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        msg = {
            "type": "message",
            "id": self.id,
            "message": parsed['message']
        }
        redis_client.publish('chat', json.dumps(msg))

    def on_close(self):
        if self in clients:
            clients.remove(self)
            if self.id in online_users:
                online_users.remove(self.id)
                message = {
                    "type": "status",
                    "message": f"Пользователь {self.id} отключился."
                }
                redis_client.publish('chat', json.dumps(message))


async def redis_listener():
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            data = json.loads(message['data'])
            for client in clients:
                try:
                    client.write_message(data)
                except:
                    pass
        await gen.sleep(0.01)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", ChatWebSocket),
    ],
        template_path="templates",
        debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(settings.APP.PORT)
    tornado.ioloop.IOLoop.current().spawn_callback(redis_listener)
    print(f"Serving on  http://{settings.APP.HOST}:{settings.APP.PORT}")
    tornado.ioloop.IOLoop.current().start()
