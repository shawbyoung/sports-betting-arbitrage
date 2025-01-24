import threading

class logger:
    level = 1
    lock = threading.Lock()

    def log(message: str, level: int):
        if logger.level < level:
            return
        with logger.lock:
            print(f"LOG: {message}")
    
    def log(message: str):
        with logger.lock:
            print(f"LOG: {message}")

    def log_warning(message: str):
        with logger.lock:
            print(f"WARNING: {message}")
        
    def log_error(message: str):
        with logger.lock:
            print(f"ERROR: {message}")