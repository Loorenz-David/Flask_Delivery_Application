import json
import os

class JSONFileManager():
    BASE_DIR = os.path.join(os.path.dirname(__file__), "../files")

    @classmethod
    def get_file_path(cls,filename):
        # Builds absolute path for a JSON file.
        return os.path.join(cls.BASE_DIR, filename)
    
    @classmethod
    def load(cls,filename):
        # Loads and returns JSON content.
        file_path = cls.get_file_path(filename)
        try:
            with open(file_path,"r") as f:
                return json.load(f)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {file_path}")

    @classmethod
    def save(cls, filename, data):
        # Writes Python data to JSON file
        file_path = cls.get_file_path(filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
