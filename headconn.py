import os
import json
import time
import queue
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
        self.imagine_prompt = []
        self.reflect_prompt = []
        self.state_record = ['idle']
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

        self.prompt_queue = queue.Queue()

        self.run_thread = threading.Thread(target=self.run)
        self.run_thread_lock = threading.Lock()

    def run(self):

        while True:
            with self.run_thread_lock:
                prompt = self.prompt_queue.get(block=True)
                print(f"self.state_record:{self.state_record[-1]}")
                if self.state_record[-1] == 'idle' \
                   and prompt['type'] == 'imagine':
                    self.imagine_client.run(prompt=prompt['value'])
                    self.prompt_queue.task_done()
                    time.sleep(3)
                    if self._fine_tune(prompt['type']) is not None:
                        self.imagine_client.run(prompt=prompt['value'])
                    else:
                        print("Append imagine")
                        self.prompt_queue.put({"type": 'reflect', 'value' : 'test'})
                        self.state_record.append(prompt['type'])
                elif self.state_record[-1] == 'imagine':
                    #self.reflect_client.run(prompt=prompt['value'])
                    #self.prompt_queue.task_done()
                    time.sleep(3)
                else:
                    time.sleep(1)

    def start(self):
        self.run_thread.start()

    def _fine_tune(self, prompt_type: str):
        instructions = input("Enter fine tuning instructions: ")
        print(f"instructions:{instructions}")
        if instructions == "":
            return None

        if prompt_type == 'imagine':
            self.imagine_prompt.append(instructions)
            print(f"self.imagine_prompt:{self.imagine_prompt}")
            #hc.prompt_queue.put({"type": 'imagine', 'value' : hc.imagine_prompt})
            return instructions

        return None


if __name__ == '__main__':
    hc = Headconn()
    imagine_prompt = input("Enter imagine prompt: ")
    hc.imagine_prompt.append(imagine_prompt)
    hc.prompt_queue.put({"type": 'imagine', 'value' : hc.imagine_prompt})
    hc.start()
