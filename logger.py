import threading

class logger:
    level = 1
    lock = threading.Lock()

    def log(level: int, message: str):
        if logger.level < level:
            return
        with logger.lock:
            print(f"LOG: {message}")
    
    def log(message: str):
        with logger.lock:
            print(f"LOG: {message}")

    def log_warning(message: str):
        print(f"WARNING: {message}")
        
    def log_error(message: str):
        print(f"ERROR: {message}")