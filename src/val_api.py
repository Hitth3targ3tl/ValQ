import io
import json
import requests
import time
import os, sys
from PIL import Image, ImageTk

class val_api:
    _agent_dict = None
    
    @staticmethod
    def agent_data():
        if val_api._agent_dict is not None:
            # Return the cached data if it exists
            return val_api._agent_dict
        
        # If cache is empty, fetch data from API
        agents_response = requests.get("https://valorant-api.com/v1/agents")

        if agents_response.status_code != 200:
            print(f"Error: {agents_response.status_code}")
            time.sleep(3)
            exit(0)
        
        agents_json = agents_response.json()['data']
        agent_dict = {}

        for agent in agents_json:
            if agent['isPlayableCharacter'] == False:
                continue
            
            agent_dict[agent['displayName']] = agent['uuid']
        
        # Cache the fetched data
        val_api._agent_dict = agent_dict
        
        print(agent_dict)  # Optional: for debugging purposes
        return agent_dict
    @staticmethod
    async def weapon_data():
        weapons_response = requests.get("https://valorant-api.com/v1/weapons").json()
        return weapons_response

    @staticmethod
    async def comp_tiers():
        tiers = requests.get("https://valorant-api.com/v1/competitivetiers").json()
        return tiers
        
