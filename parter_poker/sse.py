"""
Shameless read from https://maxhalford.github.io/blog/flask-sse-no-deps/

"""
import queue


class MessageAnnouncer:
    last_broadcast_listener_count: int = None

    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg: str):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

    def update_current_listener_count(self, new_listener_count: int) -> None:
        self.last_broadcast_listener_count = new_listener_count
        print(f"[SSE] Broadcasting to {self.last_broadcast_listener_count} clients.")


def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg
