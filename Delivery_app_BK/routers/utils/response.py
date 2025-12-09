from flask import jsonify
import json, gzip, base64

# object use for returning the router request to the front end
class Response:
    def __init__(self, status=200, short_message="", error=None, payload=None, incoming_data=None, identity=None):
        self.status: int = status
        self.short_message: str = short_message
        self.error: str = error
        self.payload = payload if payload is not None else {}
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

    def set_created_payload(self, instances, fields=None):
        if not instances:
            return self

        target_fields = list(fields) if fields else ["id"]
        payload_entries = []
        for instance in instances:
            entry = {}
            for field in target_fields:
                if hasattr(instance, field):
                    value = getattr(instance, field)
                    if value is not None:
                        entry[field] = value
            if not entry and hasattr(instance, "id"):
                entry = {"id": getattr(instance, "id")}
            if entry:
                payload_entries.append(entry)

        if not payload_entries:
            return self

        if len(payload_entries) == 1:
            self.set_payload({"instance": payload_entries[0]})
        else:
            self.set_payload({"items": payload_entries})

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
                raise ValueError("resquest data must be in dict form with format:",
                                 """
                                    {
                                        "data": { } / []
                                        "is_compress: false / true
                                    }
                                """
                                 )
                
            data = incoming_data.get('data',None)
            if data is None:
                raise ValueError("resquest data must be in dict form with format:",
                                 """
                                    {
                                        "data": { } / []
                                        "is_compress: false / true
                                    }
                                """
                                 )

            is_compress = incoming_data.get("is_compress", False)
            if not is_compress:
                return data

            compressed_bytes = base64.b64decode(data)
            json_bytes = gzip.decompress(compressed_bytes)

            return json.loads(json_bytes.decode("utf-8"))

        except Exception as e:
            self.set_message("Fail to proccess data")
            self.set_error(f"Fail to proccess data: {str(e)}", 400)
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
            self.set_message("Error when compressing data.")
            self.set_error(f"Compression failed: {str(e)}", 400)
        
        return self
