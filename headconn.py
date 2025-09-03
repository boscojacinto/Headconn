import os
import json
import time
import threading
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user, system, image, tool, tool_result

from imagine import Imagine
from reflect import Reflect

class Headconn:
    def __init__(self):
        self.work_dir = None
        self.imagine_client = None
        self.reflect_client = None
        self.scene_prompt = None
        self.work_dir = self._create_workdir()
        self.run_thread = None
        self.run_thread_lock = False

        self._initialize()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def _initialize(self) -> None:
        load_dotenv()

        self.imagine_client = Imagine()
        self.reflect_client = Reflect()

        self.run_thread = threading.Thread(target=self.run)
        self.run_thread_lock = threading.Lock()

    def run(self):

        while True:
            with self.run_thread_lock:
                if self.scene_prompt is not None:
                    self.imagine_client.run(scene_prompt=self.scene_prompt)
                    time.sleep(3)
                    self.scene_prompt = None

    def start(self):
        self.run_thread.start()


if __name__ == '__main__':
    headconn = Headconn()
    headconn.scene_prompt = input("Enter scene prompt: ")
    headconn.start()
