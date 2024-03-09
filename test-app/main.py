import lib
import requests
import site
import sys

lib.say_hi()

print(f"__file__ = {__file__}")
print(f"sys.path = {lib.pretty_list_dump(sys.path)}")
print(f"prefix = {sys.prefix}")
print(f"executable = {sys.executable}")
print(f"site-packages = {lib.pretty_list_dump(site.getsitepackages())}")

r = requests.get("http://example.com")
print(f"http request status code = {r.status_code}")

import tkinter as tk
window = tk.Tk()
window.mainloop()