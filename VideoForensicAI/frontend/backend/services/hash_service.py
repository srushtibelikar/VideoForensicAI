import hashlib

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024 * 1024)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
