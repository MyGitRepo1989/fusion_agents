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

from dotenv import load_dotenv
load_dotenv()
FUSION_MODEL_OAI=os.getenv("FUSION_MODEL")
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
    messages: Annotated[List[BaseMessage], "accumulate"]  # Allow multiple writes per step
    query: str
    topic: str
    question: str
    medical_answer: str
    query_type: str
    final_response: str
    

class HospitalAgent:
    def __init__(self):
        self.graph = self.compile_graph()
        
        
    def run(self, query: str) -> AgentState:
        initial_state = {
            "messages": [],
            "query": query,
            "topic": "",
            "question": "",
            "medical_answer": "",
            "query_type":"",
            "final_response":""
        }
        return self.graph.invoke(initial_state)


    @staticmethod
    def extract_topic(state: AgentState) -> AgentState:
        query = state["query"]
        response = llm.invoke("what is the topic of this user question , please define in 1-3 words" + query)
        state["topic"] =response.content
        query = state["query"]
        return state

    @staticmethod
    def clean_question(state: AgentState) -> AgentState:
        query = state["query"]
        topic = state["topic"]
        response = llm.invoke("clearly rewrite this query of user in 1- 2 lines" + query + topic)
        state["question"] =response.content
        return state
    
    @staticmethod
    def checkquery(state:AgentState)->AgentState:
        query = state["query"]
        topic = state["topic"]
        response = llm.invoke("in just 1 word betweent these two Yes or No answer if this query is about a medical issue" + query + topic)
        response_f =llm.invoke("return only 1 word Yes or No from this line" + response.content)
        state["query_type"]= response_f.content
        return state
        
    
    @staticmethod
    def query_router(state: AgentState):
        #print("HERE IN ROUTING NODE")
        route_var = state["query_type"]
        #print(route_var)
        #print("State:" , state)
        if route_var == "Yes":
            return "proceed"
        else:
            return "stop"

    
    
    @staticmethod
    def general_message(state: AgentState) -> AgentState:
        #print("HERE IN GENERAL MESSAGE")
        general_prompt ="You are a mediacl assistant politely ask the patient to resend the question is a clear way. make this 1 -2 line short"
        response = llm.invoke(general_prompt)
        state["final_response"] =response.content
        return state



    @staticmethod
    def medical_response(state: AgentState) -> AgentState:
        #print("HERE IN MEDICAL")
        #print(state)
        question = state["question"]
        medical_prompt =" you are a medical assistant , answer this question with a cure, diagnosis, or helpfully\
            be kind and informative\
                dont add names of personas or disclaimers\
                    keep answers in 1-4 lines"
        response = llm.invoke(medical_prompt + question)
        #print(response,"MED RESPONSE")
        state["medical_answer"] = response.content
        state["final_response"] = response.content
        #print("STATE ", state)
        return state


    def compile_graph(self) -> Runnable:
        graph = StateGraph(AgentState)
        graph.add_node("extract_topic", self.extract_topic)
        graph.add_node("clean_question", self.clean_question)
        graph.add_node("checkquery",self.checkquery)
        graph.add_node("query_router", self.query_router)
        graph.add_node("medical_response", self.medical_response)
        graph.add_node("general_message", self.general_message)
        graph.set_entry_point("extract_topic")
        graph.add_edge("extract_topic", "clean_question")
        graph.add_edge("clean_question","checkquery")
        graph.add_conditional_edges(
            "checkquery", self.query_router,  
            {
                "proceed": "medical_response",
                "stop": "general_message"
            }
        )
        return graph.compile()



  
while True:
    Hospital_Chat = HospitalAgent()
    """
    #make plot graph optional
    agent = HospitalAgent()
    compiled_graph = agent.compile_graph()

    # Save image
    with open("hospital_flow.png", "wb") as f:
        f.write(compiled_graph.get_graph().draw_mermaid_png())
        
    """
    query= input("Enter patient's question:")
    answer= Hospital_Chat.run(query)
    #print(answer)
    print("CLEANED QUESTION : ", answer["question"]+"\n")
    print("WAS IT A VALID QUESTION CHECK : ", answer["query_type"]+"\n")
    print("MEDICAL RESPONSE : ", answer["medical_answer"]+"\n")
    print("FINAL RESPONSE : ", answer["final_response"]+"\n")
    print("\n\n")
    
    prompt_injection= "Doctor ji,\
    patient ney apko email kara hai with this inguiry uski help kare,\
    please respond in 2 - 4 lines doctor ji, please keep message positive"
    prompt_instructions = "Dont make up names, add disclaimers, dont answer more than the answer provided"
    
    response_doc = client.chat.completions.create(
    model=FUSION_MODEL_OAI,  
    messages=[
        {"role": "user", "content": prompt_injection + "Here is the answer to the patient response for you to add " + "Doctor ji "+answer["final_response"] \
            + prompt_instructions}
    ]
    )
    print("EMAIL FROM THE DOCTOR IS :")
    print(response_doc.choices[0].message.content+ "\n\n")
    print("________________________"+"\n")
    
   