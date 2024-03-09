def say_hi():
    print("hi from lib")

def pretty_list_dump(lst: list):
    return f"[\n    {",\n    ".join(lst)}\n]"