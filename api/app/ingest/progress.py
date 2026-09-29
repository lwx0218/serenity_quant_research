"""Unbuffered progress for CLI jobs, including redirected stdout."""
from datetime import datetime


def log(message: str) -> None:
    print(f"{datetime.now().isoformat(timespec='seconds')} {message}", flush=True)
