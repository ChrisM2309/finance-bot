from langchain.memory import ConversationBufferMemory

conversation_memory = ConversationBufferMemory(memory_key="chat_history")

def get_conversation_memory():
    return conversation_memory