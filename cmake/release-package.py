import os
import shutil
import sys

if len(sys.argv) == 1:
    exit(-1)

dist_dir = os.path.join("dist", "python-bundler")
shutil.rmtree(dist_dir, ignore_errors=True)
os.makedirs(dist_dir)

for file in sys.argv[1:]:
    shutil.copy(file, dist_dir)

shutil.make_archive(
    dist_dir, "zip",
    root_dir=os.path.join(dist_dir, os.pardir),
    base_dir="python-bundler"
)