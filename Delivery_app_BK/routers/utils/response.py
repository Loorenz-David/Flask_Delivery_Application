from flask import jsonify
import json, gzip, base64

# object use for returning the router request to the front end
class Response:
    def __init__(self, status=200, short_message="", error="", payload=None, incoming_data=None, identity=None):
        self.status: int = status
        self.short_message: str = short_message
        self.error: str = error
        self.payload = payload if payload is not None else []
        self.is_compress: bool = False
        self.incoming_data = self.decompress_request(incoming_data)
        self.identity = identity or {}

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
    
    def decompress_request(self, incoming_data):
        if incoming_data is None:
            return None

        try:
            if not isinstance(incoming_data, dict):
                return incoming_data

            is_compress = incoming_data.get("is_compress", False)
            if not is_compress:
                return incoming_data.get("data", incoming_data)

            compressed_payload = incoming_data.get("data")
            if compressed_payload is None:
                raise ValueError("Missing compressed data payload")

            compressed_bytes = base64.b64decode(compressed_payload)
            json_bytes = gzip.decompress(compressed_bytes)

            return json.loads(json_bytes.decode("utf-8"))

        except Exception as e:
            self.set_error(f"decompression failed: {str(e)}", 500)
            return None

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
