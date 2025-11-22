import os
import getpass
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.func import entrypoint, task
from langchain_xai import ChatXAI

def _set_env(var: str):
    load_dotenv()
    if not os.getenv(var):
        os.environ[var] =  getpass.getpass(f"{var}: ")


_set_env("XAI_API_KEY")

llm = ChatXAI(model="grok-4")

#task
def generate_joke(topic: str):
	"""First LLM call to generate initial joke"""
	msg = llm.invoke(f"Write a short joke about {topic}")
	return msg.content

def check_punchline(joke: str):
	"""Gate function to check if the joke has a punchline"""
	if "?" in joke or "!" in joke:
		return "Pass"

	return "Fail"

@task
def improve_joke(joke: str):
	"""Second LLM call to improve the joke"""
	msg = llm.invoke(f"Make this joke funnier by adding wordplay: {joke}")
	return msg.content

@task
def polish_joke(joke: str):
	"""Third LLM call for final polish"""
	msg = llm.invoke(f"Make this joke funnier by adding wordplay: {joke}")
	return msg.content

@entrypoint
def prompt_chaining_workflow(topic: str):
	original_joke = generate_joke(topic).result()
	if check_punchline(original_joke) == "Pass":
		return original_joke

	improved_joke = improve_joke(original_joke).result()
	return polish_joke(improved_joke).result()


for step in prompt_chaining_workflow.stream("cats", stream_mode="updates"):
	print(step)
	print("\n")