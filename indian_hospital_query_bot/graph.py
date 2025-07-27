from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from typing import List
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.prebuilt import InjectedState, ToolNode
from langgraph.store.memory import InMemoryStore
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain.chat_models import init_chat_model
import os

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_A")
os.environ["OPENAI_API_KEY"]= OPENAI_API_KEY


from openai import OpenAI
client = OpenAI()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# If API key is not set, prompt the user to enter it
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file")


#llm1 = ChatOpenAI(model="gpt-4o", temperature=0.5)
llm = init_chat_model("gpt-4o-mini", model_provider="openai",temperature=0.8)


from typing import TypedDict, List
from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable



class AgentState(TypedDict):
    messages: List[BaseMessage]
    query: str
    topic: str
    question :str
    medical_response: str

class HospitalAgent:
    def __init__(self):
        self.graph = self._compile_graph()

    @staticmethod
    def extract_topic(state: AgentState, user_input) -> AgentState:
        query = state["query"]
        response = llm.invoke("what is the topic of this user question , please define in 1-3 words" + query)
        state["topic"] =response.content
        query = state["query"]
        return state

    @staticmethod
    def clean_question(state: AgentState) -> AgentState:
        query = state["query"]
        response = llm.invoke("clearly rewrite this query of user" + query)
        state["question"] =response.content
        return state

    @staticmethod
    def medical_response(state: AgentState) -> AgentState:
        question = state["question"]
        medical_prompt =" you are a medical assistant , answer this question with a cure, diagnosis, or helpfully\
            be kind and informative\
                dont add names of personas or disclaimers\
                    keep answers in 1-4 lines"
        response = llm.invoke(medical_prompt + question)
        state["medical_response"] =response.content
        return state


    def _compile_graph(self) -> Runnable:
        graph = StateGraph(AgentState)
        graph.add_node("extract_topic", self.extract_topic)
        graph.add_node("clean_question", self.clean_question)
        graph.add_node("medical_response", self.medical_response)

        graph.set_entry_point("extract_topic")
        graph.add_edge("extract_topic", "clean_question")
        graph.add_edge("clean_question", "medical_response")

        return graph.compile()

  
