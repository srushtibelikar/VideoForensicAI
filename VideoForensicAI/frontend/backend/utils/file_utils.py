import os
import uuid

def generate_unique_filename(original_filename):
    extension = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex}{extension}"

def allowed_file(filename, allowed_extensions):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions
