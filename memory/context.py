from langchain.memory import ConversationBufferMemory

conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
    )

def get_conversation_memory():
    return conversation_memory