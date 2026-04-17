import os
import psutil
import re
import datetime
import time
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURATION ---
os.environ["OPENAI_API_KEY"] = "sknA"
KNOWLEDGE_FILE = "vm_state_log.txt"

# --- 2. SECURITY LAYER (Redactor) ---
def redact_sensitive_info(text: str) -> str:
    """Secret keys aur IPs ko hide karne ke liye logic"""
    # IP Addresses mask karna
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'XX.XX.XX.XX', text)
    # API Keys / Passwords mask karna
    text = re.sub(r'(?i)(password|secret|key|token|auth|sk-)[ :=]*[^\s]+', r'\1: [REDACTED]', text)
    return text

# --- 3. DATA COLLECTOR (Snapshot) ---
def take_vm_snapshot():
    """VM ki current health ka data nikalna"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    # Top 5 CPU consuming processes
    procs = sorted(psutil.process_iter(['name', 'cpu_percent']),
                   key=lambda x: x.info['cpu_percent'], reverse=True)[:5]
    proc_list = ", ".join([f"{p.info['name']}({p.info['cpu_percent']}%)" for p in procs])

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"[{timestamp}] CPU: {cpu}%, MEM: {mem}%, TopProcs: {proc_list}"

    # Secure it before saving
    safe_report = redact_sensitive_info(report)

    # Append to local knowledge base
    with open(KNOWLEDGE_FILE, "a") as f:
        f.write(safe_report + "\n")
    print(f"📊 Snapshot saved: {safe_report}")

# --- 4. RAG & AI LOGIC ---
def ask_vm_expert(question: str):
    """Local context use karke AI se jawab mangna"""
    if not os.path.exists(KNOWLEDGE_FILE):
        return "No data collected yet."

    # Context Retrieval (Last 20 lines for recent state)
    with open(KNOWLEDGE_FILE, "r") as f:
        context_lines = f.readlines()[-20:]
    context_text = "".join(context_lines)

    # LangChain Prompt
    prompt = ChatPromptTemplate.from_template("""
    You are a DevOps Site Reliability Engineer (SRE).
    Below are the recent heartbeats/snapshots from a Linux VM.

    Context:
    {context}

    User Question: {question}

    Constraint: If the user asks for a solution, provide a CLI command.
    If you see [REDACTED], ignore that specific value but acknowledge the process.
    """)

    model = ChatOpenAI(model="gpt-4o", temperature=0)
    chain = prompt | model | StrOutputParser()

    return chain.invoke({"context": context_text, "question": question})

# --- 5. MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    print("🤖 VM Agent Started... (Press Ctrl+C to stop)")

    # Example: Pehle ek snapshot lete hain
    take_vm_snapshot()

    # User Interactivity
    while True:
        mode = input("\nChoose: [1] Take Snapshot | [2] Ask AI | [3] Exit: ")

        if mode == "1":
            take_vm_snapshot()
        elif mode == "2":
            query = input("Puchiye (e.g., 'Is there any memory spike?'): ")
            print("\n🤖 AI is thinking...")
            print("-" * 30)
            print(ask_vm_expert(query))
            print("-" * 30)
        elif mode == "3":
            break
        else:
            print("Invalid choice!")
