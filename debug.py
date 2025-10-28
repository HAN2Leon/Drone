def try_to_run(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error has occured in fonction {func.__name__} ：{e}")
            return None  
    return wrapper