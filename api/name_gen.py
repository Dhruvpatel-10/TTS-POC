import uuid

def generate_strong_name():
    """Return a strong random name of 10 characters using uuid."""
    return uuid.uuid4().hex[:12]