# app/entrypoint.py

import os
import subprocess

if os.environ.get("RUN_TESTS") == "1":
    print("🧪 Running test suite inside container...")
    subprocess.run(["pytest", "tests"], check=True)
else:
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
