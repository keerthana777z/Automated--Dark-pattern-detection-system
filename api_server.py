from fastapi import FastAPI
from monitor import run_monitoring_cycle

app = FastAPI()


@app.get("/run-monitor")
def run_monitor():
    try:
        messages = run_monitoring_cycle()

        return {
            "status": "monitor executed",
            "output": messages
        }

    except Exception as e:
        return {
            "status": "error",
            "output": str(e)
        }