import sys

from src.valclient.client import Client

client = Client(region='eu')
client.activate()
            
session_state =client.session_fetch()
print(session_state)
'''loopStates:
    MENUS
    PREGAME
    INGAME
    '''