from flask import jsonify
import json, gzip, base64

# object use for returning the router request to the front end
class Response():

    def __init__(self,status=200,short_message="",error="", payload=[]):

        self.status:int = status
        self.short_message:str = short_message
        self.error:str = error
        self.payload:list = payload
        self.is_compress:bool = False
        

    def set_message(self,message):
        self.short_message = message
        return self
    

    def set_error(self,message,status=400):
        self.error = message
        self.status = status
        return self
    
    
    def set_payload(self,data):
        self.payload = data
        return self
    

    def build(self):
        return jsonify({
            "status": self.status,
            "message":self.short_message,
            "error":self.error,
            "data":self.payload,
            "is_compress":self.is_compress
        }), self.status
    

    def compress_payload(self):
        try:
            # Safely convert payload to bytes
            json_bytes = json.dumps(self.payload).encode('utf-8')

            # Compress using gzip
            compressed = gzip.compress(json_bytes)

            # Base64-encode to make it safe to transport in JSON
            compressed_b64 = base64.b64encode(compressed).decode('utf-8')

            # Replace payload with compressed data
            self.payload = compressed_b64

            self.is_compress = True
        
        except Exception as e:
            self.set_error(f"Compression failed: {str(e)}", 500)
        
        return self