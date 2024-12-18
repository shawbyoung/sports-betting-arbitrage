class logger:
    level = 1
    
    def log(level: int, message: str):
        # implement level logging to avoid to much io.
        if logger.level >= level:
            print(f"LOG: {message}")
    
    def log(message: str):
        print(f"LOG: {message}")

    def log_error(message: str):
        print(f"ERROR: {message}")