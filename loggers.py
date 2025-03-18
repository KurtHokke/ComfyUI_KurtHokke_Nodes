import inspect
import logging
import time
from functools import wraps

#logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')

def setup_logger(name: str, log_file: str = "app.log", level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
    return logger

def get_logger(name: str, level: int = logging.DEBUG):
    logger = setup_logger("logger", level=level)
    if name == "log_return" or name == "return":
        return log_return(logger)
    elif name == "log_function" or name == "function":
        return log_function(logger)
    elif name == "log_all" or name == "all":
        return logger, log_all_methods(logger)
    else:
        raise ValueError(f"Invalid decorator: {name}")

def log_return(logger):
    """A method-level decorator to log method name, args, kwargs, return value, and execution time."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Log method start
            logger.debug(f"Calling method: {fn.__qualname__} (in {args[0].__class__.__name__ if args else ''})")

            # Log arguments (with variable names)
            sig = inspect.signature(fn)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            logger.debug(f"  Args/kwargs: {dict(bound_args.arguments)}")

            # Measure execution time
            start_time = time.time()
            result = fn(*args, **kwargs)
            end_time = time.time()

            # Log return value and execution time
            logger.debug(f"  Returned: {result}")
            logger.debug(f"  Execution time: {end_time - start_time:.6f} seconds")
            return result

        return wrapper

    return decorator

def log_all_methods(logger):
    """Class-level decorator to apply logging to all callable attributes in a class."""
    def decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):  # Check if it's a method
                setattr(cls, attr_name, log_return(logger)(attr_value))
        return cls
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


