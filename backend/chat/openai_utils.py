from pathlib import Path
import json
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def load_knowledge_base():
    """
    Loads all JSON files from chat/data/ into a combined list.
    Each file should contain either a list or a single dict.
    """
    base_path = Path(settings.BASE_DIR) / "chat" / "data"
    knowledge = []

    for file in base_path.glob("*.json"):
        try:
            data = json.load(file.open())
            if isinstance(data, list):
                knowledge.extend(data)
            elif isinstance(data, dict):
                knowledge.append(data)
        except Exception as e:
            print(f"Error loading {file.name}: {e}")
    return knowledge

def get_openai_response(user_message):
    """
    Constructs a system prompt using the loaded knowledge base
    and sends a user message to OpenAI.
    """
    context_blocks = load_knowledge_base()
    system_content = "You are a helpful assistant on MatthewRaynor.com. Use the following context when answering questions:\n\n"

    for block in context_blocks:
        title = block.get('title') or 'Untitled'
        content = block.get('content') or ''
        system_content += f"- {title}: {content}\n"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content.strip()
