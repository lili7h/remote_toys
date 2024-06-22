import asyncio
import os
import time

import sass
from threading import Lock, Thread
from asyncio import sleep, timeout, gather
from buttplug import Client, WebsocketConnector, ProtocolSpec, Device, DisconnectedError
from tqdm import tqdm
from flask import Flask, request, jsonify, render_template, Response

from parter_poker.sse import MessageAnnouncer, format_sse


app = Flask(__name__)
announcer = MessageAnnouncer()


class Singleton(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Vibrator(metaclass=Singleton):
    client: Client = None
    connector: WebsocketConnector = None
    # Cache the devices one layer up rather than having to reach into the client every time
    devices: list[Device] = None
    # This agent controls all the ThreadedActors that the Vibrator class instantiates
    # Current intensity value (inclusive of ambient and instant)
    current_vibration: float = None
    # intensity status bar
    pbar: tqdm = None

    async def connect_and_scan(self) -> None:
        assert self.connector is not None

        # If this succeeds, we'll be connected. If not, we'll probably have some
        # sort of exception thrown of type ButtplugError.
        try:
            await self.client.connect(self.connector)
            print("Connected to intiface!")
        except Exception as e:
            print(f"Could not connect to server, exiting: {e}")
            return

        if len(self.client.devices) == 0:
            print(f"Scanning for devices now, see you in 10s!")
            await self.client.start_scanning()
            await sleep(10)
            await self.client.stop_scanning()
            print(f"Done.")
        else:
            print(f"Found devices connected, assuming no scan needed.")

        if len(self.client.devices) > 0:
            print(f"Found {len(self.client.devices)} devices!")
            self.devices = [self.client.devices[x] for x in self.client.devices]
        else:
            print(f"Found no devices :(")

    def __init__(self, ws_host: str = "localhost", port: int = 12345):
        self.client = Client("Partner :3", ProtocolSpec.v3)
        self.connector = WebsocketConnector(f"ws://{ws_host}:{port}")
        self.current_vibration = 0.0
        self.devices = []

    async def _apply_intensity(self) -> None:
        futures = []
        for dev in self.devices:
            for r_act in dev.actuators:
                futures.append(r_act.command(self.current_vibration))
        try:
            async with timeout(0.5):
                await gather(*futures, return_exceptions=True)
        except DisconnectedError:
            print("Disconnected")
        except TimeoutError:
            print("Timed-out")

    async def issue_command(self):
        """
        Sets all actuators in all devices to the given intensity
        """
        # if not self.client.connected:
            # print("Tried to issue command while 'Not connected'!")
            # await self.client.connect(self.connector)

        if self.current_vibration is not None:
            await self._apply_intensity()

    def set_intensity(self, new_intensity: float) -> None:
        self.current_vibration = max(0.0, min(1.0, new_intensity))
        msg = format_sse(data=f'{{"intensity": {int(self.current_vibration * 100)}}}', event='newIntensity')
        announcer.announce(msg=msg)
        update_listener_count()


def update_listener_count() -> None:
    _cnt = int(len(announcer.listeners))
    if _cnt != announcer.last_broadcast_listener_count:
        msg = format_sse(data=f'{{"listeners": {_cnt}}}', event='newListener')
        announcer.announce(msg=msg)
        announcer.update_current_listener_count(_cnt)


@app.route("/toy/intensity", methods=['GET', 'POST'])
def set_intensity():
    _inst = Vibrator()
    if request.method == 'POST':
        _data = request.get_json()
        _inst.set_intensity(float(int(_data['intensity']) / 100))
        return {}, 200
    else:
        return jsonify({'intensity': int(_inst.current_vibration * 100)}), 200


@app.route('/listen', methods=['GET'])
def listen():
    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    update_listener_count()
    return Response(stream(), mimetype='text/event-stream')


@app.route("/")
def index():
    print(os.getcwd())
    return render_template('index.html')


def apply_intensity(vibrator: Vibrator, loop: asyncio.AbstractEventLoop) -> None:
    time.sleep(2)
    while True:
        time.sleep(0.1)
        loop.run_until_complete(vibrator.issue_command())


def myapp():
    sass.compile(dirname=('static/sass', 'static/css'), output_style='compressed')

    _loop = asyncio.new_event_loop()
    _inst = Vibrator()
    _loop.run_until_complete(_inst.connect_and_scan())

    _thread = Thread(target=apply_intensity, args=(_inst, _loop,), daemon=True)
    _thread.start()

    return app


def devapp():
    _app = myapp()
    return _app


if __name__ == "__main__":
    devapp()
