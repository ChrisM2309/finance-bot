is_abaco_client = False

def set_is_abaco_client(state):
    global is_abaco_client
    is_abaco_client = state
    print(f"From is_client, {is_abaco_client}")
    
def get_is_abaco_client():
    return is_abaco_client