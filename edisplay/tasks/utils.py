from functools import wraps

def auto_handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'{func.__name__} raised an exception but it was handled {e}')
            return {f'error-{func.__name__}': e}
    return wrapper