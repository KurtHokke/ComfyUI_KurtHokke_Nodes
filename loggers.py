import logging
from functools import wraps

def setup_logger(name: str, log_file: str = "app.log", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # Avoid adding multiple handlers if the logger already has any
    if not logger.handlers:
        logger.addHandler(file_handler)
    return logger

def get_logger(name: str):
    if name == "log_return":
        return log_return(setup_logger(name))
    elif name == "log_function":
        return log_function(setup_logger(name))
    elif name == "log_all":
        return setup_logger(name), log_all_methods(setup_logger(name))
    else:
        raise ValueError(f"Invalid decorator: {name}")

def log_return(logger):
    """Decorator to log function/method return values."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)  # Call the original function
            logger.info(f"{func.__name__} returned: {result}")  # Log the return value
            return result  # Return the result as usual
        return wrapper
    return decorator

def log_function(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting {func.__name__}...")
            logger.info(f"Arguments: args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)  # Call the actual function
            logger.info(f"{func.__name__} finished.")
            if result is not None:  # Log the return value if one exists
                logger.info(f"Returned: {result}")
            return result

        return wrapper

    return decorator

def log_all_methods(logger):
    """Class-level decorator to log return values of all methods."""
    def decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):  # Check if it's a method
                setattr(cls, attr_name, log_return(logger)(attr_value))
        return cls
    return decorator