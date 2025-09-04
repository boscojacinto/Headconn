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
from compose_v2 import Compose

class Headconn:
    def __init__(self):
        self.work_dir = None
        self.imagine_client = None
        self.reflect_client = None
        self.compose_client = None
        self.imagine_prompt = []
        self.images = []
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
        self.compose_client = Compose()

        self.prompt_queue = queue.Queue()

        self.run_thread = threading.Thread(target=self.run)
        self.run_thread_lock = threading.Lock()

    def run(self):

        while True:
            with self.run_thread_lock:
                prompt = self.prompt_queue.get(block=True)
                if self.state_record[-1] == 'idle' and prompt['type'] == 'imagine':
                    if self.imagine_client.run(prompt=prompt['value']) is False:
                        self.state_record.append({'agent': prompt['type'], 'execution': 'failed'})
                    else:
                        if self._fine_tune(prompt['type']) is not None:
                            self.imagine_client.fine_tune(prompt=prompt['value'])
                        else:
                            if all(map(lambda x: x['complete'] if x['complete'] is True else False, self.imagine_client.results)) is False:
                               self.state_record.append({'agent': prompt['type'], 'execution': 'failed'}) 
                            else:
                                for result in self.imagine_client.results:
                                    self.prompt_queue.put({"type": 'reflect', 'value' : {
                                        'image_path': result['output']['image_file'], 'prompt': result['output']['query']}})
                                self.state_record.append(prompt['type'])

                    self.prompt_queue.task_done()

                elif self.state_record[-1] == 'imagine' or self.state_record[-1] == 'reflect':
                    if self.prompt_queue.qsize() == 0 or self.prompt_queue.qsize() == 1:
                        self.reflect_client.run(image_path=prompt['value']['image_path'], prompt=prompt['value']['prompt'])
                        self.images.append(prompt['value']['image_path'])
                        self.prompt_queue.task_done()
                        self.state_record.append(prompt['type'])
                        if self.prompt_queue.qsize() == 0:
                            if self.compose_client.run(first_image=self.images[0],
                                second_image=self.images[1], prompt=self.imagine_prompt[0]) is True:
                                self.prompt_queue.put({"type": 'compose', "complete": True,
                                    'value' : {'image_path': self.compose_client.images[0]}})
                                self.state_record.append('compose')
                            else:
                                self.prompt_queue.put({"type": 'compose', "complete": False,
                                    'value' : {'image_path': self.compose_client.images[0]}})                                
                                self.state_record.append('compose')
                    time.sleep(3)
                elif self.state_record[-1] == 'compose':
                    if prompt['complete'] == True:
                        print("Done.")
                    else:
                        print("Failed.")
                    exit()
                else:
                    time.sleep(1)

    def start(self):
        self.run_thread.start()

    def _fine_tune(self, prompt_type: str):
        instructions = input("Enter fine tuning instructions: ")
        if instructions == "":
            return None

        if prompt_type == 'imagine':
            self.imagine_prompt.append(instructions)
            #hc.prompt_queue.put({"type": 'imagine', 'value' : hc.imagine_prompt})
            return instructions

        return None


if __name__ == '__main__':
    hc = Headconn()
    imagine_prompt = input("Enter imagine prompt: ")
    hc.imagine_prompt.append(imagine_prompt)
    hc.prompt_queue.put({"type": 'imagine', 'value' : imagine_prompt})
    hc.start()
