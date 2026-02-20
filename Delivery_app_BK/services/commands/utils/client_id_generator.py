from uuid import uuid4

def generate_client_id(label=None):
    uui_id = uuid4().hex 
    clien_id = ''

    if label:
        return f"{label}_{uui_id}"
    
    return uui_id