import os
import sys
import requests
from tkinter import ttk, messagebox
from tkinter import *
import tkinter as tk
import sv_ttk
from PIL import Image, ImageTk
import io
import threading
from concurrent.futures import ThreadPoolExecutor
from src.constants import *
from src.region import get_region
from src.valclient.client import Client
from src.valclient.exceptions import *
from src.val_api import val_api
import queue
import time
import random



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./")
    return os.path.join(base_path, relative_path)

region = get_region()

if region[1][1] not in list(data["regions"].values()):
    print("Invalid region, make sure Valorant is open")
    sys.exit()

try:
    counter = 0
    while counter < 6:
        try:
            region = get_region()
            client = Client(region=region[1][1])
            client.activate()
            break
        except HandshakeError:
            print('waiting for val')
            if counter == 5:
                print('Waiting for Val')
                counter = 0
            time.sleep(5)
            counter =+ 1
except Exception as e:
    print(e)
    sys.exit()

class ui(tk.Tk):
    def __init__(self, title, size):
        super().__init__()

        # self.overrideredirect(1)
        self.attributes('-toolwindow', True)
        self.attributes('-topmost', True)

        # Main window settings
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])
        self.maxsize(size[0], size[1]) 
        # Initialize frames
        self.agent_frame_instance = agent_frame(self)  # Create a single instance of agent_frame
        
        # Initially show the center_frame and agent_frame_instance in Agent and Instalock tabs
        self.agent_frame_instance.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        sv_ttk.set_theme("dark")
        self.mainloop()

class agent_frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.agents = val_api.agent_data()
        self.agent_buttons = {}
        self.queue = queue.Queue()

        # Create the loading label
        self.loading_label = ttk.Label(self, text="Loading agents...", font=("Arial", 12))
        self.loading_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Create the progress bar
        self.progress_bar = ttk.Progressbar(self, mode='determinate', maximum=len(self.agents))
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=10)

        self.thread = threading.Thread(target=self.create_widgets)
        self.thread.start()

        # Initialize the button (will be updated later)
        self.lock_button = ttk.Button(self, text="Lock", command=self.lock_agent)
        self.lock_button.grid(row=0, column=0, columnspan=2, pady=10)

        self.random_button = ttk.Button(self, text="Lock random", command=self.random_agent)
        self.random_button.grid(row=14, column=0, columnspan=2, pady=0)
        
        self.dodge_button = ttk.Button(self, text="Dodge Queue", command=self.dodge_queue)
        self.dodge_button.grid(row=15, column=0, columnspan=2, pady=10)
        
    def dodge_queue(self):
        client.pregame_quit_match()
        print('Dodged queue')
        
    def fetch_image(self, agent_name, agent_id):
        image_url = f"https://media.valorant-api.com/agents/{agent_id}/displayiconsmall.png"
        response = requests.get(image_url)
        image_data = response.content

        # Create a file-like object in memory from the response content
        image_file = io.BytesIO(image_data)

        # Create a PIL image from the file-like object
        pil_image = Image.open(image_file, formats=["PNG"])
        pil_image.load()

        # Resize the image to 30x30 pixels
        resized_image = pil_image.resize((35, 35), resample=Image.NEAREST)

        # Convert the resized PIL image to a Tkinter-compatible image
        tk_image = ImageTk.PhotoImage(resized_image)

        return agent_name, tk_image

    def create_widgets(self):
        # Use a thread pool to fetch images concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(lambda item: self.fetch_image(*item), self.agents.items())

        # Schedule GUI updates on the main thread
        self.after(0, self.update_widgets, results)

    def update_widgets(self, results):
        progress = 0
        for agent_name, tk_image in results:
            # Create the button with image
            button = ttk.Button(self, image=tk_image, command=lambda name=agent_name: self.select_agent(name))
            button.image = tk_image  # Keep a reference to avoid garbage collection
            self.agent_buttons[agent_name] = button

            # Update the progress bar
            progress += 1
            self.progress_bar['value'] = progress

        # Remove the loading label and progress bar
        self.loading_label.grid_forget()
        self.progress_bar.grid_forget()

        # Layout the buttons
        row = 0
        col = 0
        for button in self.agent_buttons.values():
            button.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Place the button initially
        self.lock_button.grid(row=len(self.agent_buttons) // 2 + 1, column=0, columnspan=2, pady=10)

    def select_agent(self, agent):
        
        if client.session_fetch()['loopState'] != "PREGAME":
            print("Can't select agent because you're not in a pre-game")
        else:
            try:
                self.agent = self.agents[agent]
                print(f"Selected agent: {self.agent}")
                client.pregame_select_character(agent_id=self.agent)
            except PhaseError:
                print("Can't select agent because you're not in a pre-game")
                self.agent = NONE
        
    def lock_agent(self):
        if client.session_fetch()['loopState'] != "PREGAME":
            print("Can't select agent because you're not in a pre-game")
        else:
            try:
                if self.agent != NONE:
                    client.pregame_lock_character(self.agent)
                    print(f'Agent locked in: {self.agent}')
                else:
                    print("Can't lock agent because you haven't selected an agent")
            except NameError:
                print("Can't lock agent because you haven't selected an agent")

    def instalock(self):
        try:
            if self.agent != NONE:
                self.instalock_tab.begin_instalock(self.agent)
                print(f'Instalocked agent: {self.agent}')
            else:
                print("Can't instalock because you haven't selected an agent")
        except NameError:
            print("Can't instalock because you haven't selected an agent")
    def random_agent(self):
        self.agents = val_api.agent_data()
        if not self.agents:
            return "No more agents available!"
        
        agent_counter = 0
        delay = 0
        
        while agent_counter < 5:
            
            selected_agent = random.choice(list(self.agents.keys()))
            print(selected_agent)
            self.select_agent(selected_agent)
            
            del self.agents[selected_agent]
            
            time.sleep(delay)
            delay += (0.1 + random.uniform(0.5, 0.12))
            print(agent_counter)
            if agent_counter == 4:
                client.pregame_lock_character(self.agent)
            agent_counter += 1
        return selected_agent
ui(f"ValQ v{version}", (127, 820))
