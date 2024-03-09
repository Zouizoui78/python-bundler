import os
from pathlib import Path
import shutil
import sys

if len(sys.argv) == 1:
    exit(-1)

dist_dir = Path(os.path.join("dist", "python-launcher"))
dist_dir.mkdir(parents=True, exist_ok=True)

for file in sys.argv[1:]:
    shutil.copy(file, dist_dir)

shutil.make_archive(dist_dir, "zip", dist_dir)