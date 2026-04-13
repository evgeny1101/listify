import tarfile
import os
from datetime import datetime

FILES = [
    "main.py",
    "config.py",
    "requirements.txt",
    "Dockerfile",
    ".dockerignore",
    "bot/__init__.py",
    "bot/commands.py",
    "bot/formatters.py",
    "bot/run.py",
    "bot/logging_config.py",
    "handlers/__init__.py",
    "handlers/add.py",
    "handlers/commands.py",
    "handlers/delete.py",
    "handlers/list.py",
    "database/__init__.py",
    "database/db.py",
    "keyboards/__init__.py",
    "keyboards/confirm.py",
    "keyboards/cancel.py",
    "middlewares/__init__.py",
    "middlewares/access_check.py",
    "middlewares/auto_logging.py",
    "middlewares/fsm_interrupter.py",
    "models/__init__.py",
    "models/note.py",
]

def pack():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"listify-deploy-{timestamp}.tar.gz"
    
    with tarfile.open(archive_name, "w:gz") as tar:
        for f in FILES:
            if os.path.exists(f):
                tar.add(f, arcname=f)
            else:
                print(f"WARNING: {f} not found")
    print(f"Created: {archive_name}")

if __name__ == "__main__":
    pack()