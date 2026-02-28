from openai import OpenAI
import json
from core.config import settings 


conversation=[{"role":"system","content":"u are a admin of university system user is the admin worker for university"}]
client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = settings.nvidia_key
)

async def ask(message, role="user"):
    global conversation
    conversation.append({"role": role, "content": message})
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=conversation,
        
    )
    
    assistant_msg = completion.choices[0].message
    conversation.append(assistant_msg)
    return assistant_msg.content
