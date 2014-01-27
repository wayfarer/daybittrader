import json
import websocket


__author__ = 'wayfarer'
__version__ = '0.1'


class PusherClient(websocket.WebSocket):
    def __init__(self, app_id, **kwargs):
        super(PusherClient, self).__init__(**kwargs)
        pusher_ws_url = 'wss://ws.pusherapp.com/app/%s?protocol=6&client=py&version=%s' % (app_id, __version__)
        self.connect(pusher_ws_url)
    
    def subscribe(self, channel):
        subscribe_dict = {'event': 'pusher:subscribe', 'data': {'channel': channel}}
        return self.send(json.dumps(subscribe_dict))
    
    def get_data(self):
        data_json = self.recv()
        data_dict = json.loads(data_json)
        event = data_dict['event']
        try:
            data = json.loads(data_dict['data'])
        except TypeError:
            data = data_dict['data']
        return (event, data)