import base64
import json
import sys
from valclient.client import Client
from region import get_region

region = get_region()

try:
    client = Client(region=region[1][1])
    client.activate()
except Exception:
    print('Valorant needs to be open')
    sys.exit()
class game_state:
    def get_presence():
        presences = client.fetch_presence()
        return presences

    def get_game_state(self, presences):
        return self.get_private_presence(presences)["sessionLoopState"]

state = game_state()
presence = game_state.get_presence()
state.get_game_state(presence)