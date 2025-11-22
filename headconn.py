# headconn.py
import os
import json
import time
from pathlib import Path
from typing import Literal, List, TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from imagine import Imagine
from reflect import Reflect
from compose_v2 import Compose

# Define the state of the graph
class AgentState(TypedDict):
    prompt: str
    imagine_results: List[dict]
    chosen_images: List[str]
    final_image: str
    error: str

class Headconn:
    def __init__(self):
        self.work_dir = None
        self.imagine_client = None
        self.reflect_client = None
        self.compose_client = None
        self.work_dir = self._create_workdir()
        self._initialize()
        self.app = self._build_graph()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def _initialize(self) -> None:
        load_dotenv()
        self.imagine_client = Imagine()
        self.reflect_client = Reflect()
        self.compose_client = Compose()

    def imagine_node(self, state: AgentState):
        print(f"---IMAGINE NODE---")
        prompt = state['prompt']
        try:
            success = self.imagine_client.run(prompt=prompt)
            if not success:
                return {"error": "Imagine failed"}
            
            # Extract results from imagine client
            # The imagine client stores results in self.imagine_client.results
            # We need to make sure they are in the format expected by reflect
            # Based on original code: 
            # {'complete': True, 'output': {'query': query, 'image_file': image_file, 'image_count': image_count}}
            
            results = []
            if all(map(lambda x: x.get('complete', False), self.imagine_client.results)):
                 for result in self.imagine_client.results:
                    results.append({
                        'image_path': result['output']['image_file'],
                        'image_count': result['output']['image_count'],
                        'prompt': result['output']['query']
                    })
                 return {"imagine_results": results}
            else:
                 return {"error": "Imagine failed (incomplete results)"}

        except Exception as e:
            return {"error": f"Imagine exception: {str(e)}"}

    def reflect_node(self, state: AgentState):
        print(f"---REFLECT NODE---")
        imagine_results = state.get('imagine_results', [])
        if not imagine_results:
            return {"error": "No imagine results to reflect on"}
        
        chosen_images = []
        try:
            for res in imagine_results:
                self.reflect_client.run(
                    image_path=res['image_path'],
                    image_count=res['image_count'],
                    prompt=res['prompt']
                )
                # reflect_client.image_choice is 0 or 1
                # original code: image_id = prompt['value']['image_path'] + '_' + str(image_id)
                image_id = f"{res['image_path']}_{self.reflect_client.image_choice}"
                chosen_images.append(image_id)
            
            return {"chosen_images": chosen_images}
        except Exception as e:
             print(f"Reflect node error: {e}")
             return {"error": f"Reflect exception: {str(e)}"}

    def compose_node(self, state: AgentState):
        print(f"---COMPOSE NODE---")
        chosen_images = state.get('chosen_images', [])
        prompt = state.get('prompt', "")
        
        if len(chosen_images) < 2:
             return {"error": "Not enough images to compose"}

        try:
            success = self.compose_client.run(
                first_image=chosen_images[0],
                second_image=chosen_images[1],
                prompt=prompt 
            )
            
            if success:
                return {"final_image": self.compose_client.images[-1]}
            else:
                return {"error": "Compose failed"}
        except Exception as e:
            print(f"Compose node error: {e}")
            return {"error": f"Compose exception: {str(e)}"}

    def should_continue(self, state: AgentState) -> Literal["reflect", "compose", END]:
        if state.get("error"):
            return END
        return "reflect" # This logic is for imagine -> reflect, need another for reflect -> compose

    def should_continue_reflect(self, state: AgentState) -> Literal["reflect", END]:
        if state.get("error"):
            return END
        return "reflect"

    def should_continue_compose(self, state: AgentState) -> Literal["compose", END]:
        if state.get("error"):
            return END
        return "compose"

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("imagine", self.imagine_node)
        workflow.add_node("reflect", self.reflect_node)
        workflow.add_node("compose", self.compose_node)

        workflow.set_entry_point("imagine")

        workflow.add_conditional_edges(
            "imagine",
            self.should_continue_reflect,
            {
                "reflect": "reflect",
                END: END
            }
        )
        
        workflow.add_conditional_edges(
            "reflect",
            self.should_continue_compose,
            {
                "compose": "compose",
                END: END
            }
        )
        
        workflow.add_edge("compose", END)

        return workflow.compile()

    def run(self, prompt: str):
        initial_state = {"prompt": prompt, "imagine_results": [], "chosen_images": [], "final_image": "", "error": ""}
        result = self.app.invoke(initial_state)
        return result

if __name__ == "__main__":
    headconn = Headconn()
    result = headconn.run("Harry Potter and Ron Weasley in a flying Tesla Roadster.")
    print(result)