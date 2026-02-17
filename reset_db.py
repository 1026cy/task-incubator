import os

db_path = "task_incubator.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted {db_path}")
else:
    print(f"{db_path} not found")
