import lib
import requests
import site
import sys

lib.say_hi()

print(f"sys.argv = {sys.argv}")
print(f"__file__ = {__file__}")
print(f"sys.path = {sys.path}")
print(f"prefix = {sys.prefix}")
print(f"executable = {sys.executable}")
print(f"site-packages = {site.getsitepackages()}")

r = requests.get("http://example.com")
print(f"http request status code = {r.status_code}")

if "test" in sys.argv:
    print("'test' arg received")

if "tkinter" in sys.argv:
    import tkinter as tk
    window = tk.Tk()
    window.mainloop()