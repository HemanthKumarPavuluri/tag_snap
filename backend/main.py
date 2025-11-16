

from fastapi import FastAPI

# Try importing as module first (for local dev), then as direct import (for container)
try:
    from backend.signed_urls import router as signed_router
except ImportError:
    from signed_urls import router as signed_router


app = FastAPI()
app.include_router(signed_router)


def main():
    # kept for compatibility if someone wants to call main()
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
