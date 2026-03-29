#  Customer Support Agent

# Step 1
# Importing Libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from database import init_db, get_chat_history, save_message, create_session
import uuid
from langchain_core.tools import tool

# step 2
# setup

app=FastAPI()
llm=ChatOllama(model="llama3.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"],allow_credentials=True,allow_headers=["*"],allow_methods=["*"])
app.mount("/frontend",StaticFiles(directory="../frontend"), name="frontend")
init_db()


# step 3
# Wikipedia RAG
wikipedia=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()) 

# step 4
# Memory
memory_store={}


# Step 5
# Data
system_prompt = """You are a helpful customer support agent.
You help customers with their questions and problems.
Use Wikipedia tool when you need extra information.
Be polite, professional and helpful."""

# step 6
# tools
@tool
def search_wikipedia(query: str)->str:
    """search wikipedia for any information"""
    return wikipedia.run(query)


# step 7
# Register Tool and create agent

tools=[search_wikipedia]
agent=create_react_agent(llm,tools=tools,prompt=system_prompt)


# step 8
# Chat Request model
class ChatRequest(BaseModel):
    message: str
    session_id: str=None



# Step 9
# Routes
@app.get("/")
def read_root():
    return {"message": "Customer Support Agent is running!"}

@app.get("/new_session")
def new_session():
    session_id = str(uuid.uuid4())
    create_session(session_id)
    return {"session_id": session_id}


# Step 10
# Chat Route
@app.post("/chat")
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    create_session(session_id)
    
    save_message(session_id, "user", request.message)
    
    history = get_chat_history(session_id)
    messages = []
    for role, content in history:
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    
    response = agent.invoke({"messages": messages})
    reply = response["messages"][-1].content
    
    save_message(session_id, "assistant", reply)
    
    return {"reply": reply, "session_id": session_id}

# Step 11
# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)