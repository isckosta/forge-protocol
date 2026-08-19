def create_username(name: str) -> str:
    if not name:
        raise ValueError("username must not be empty")
    return name
