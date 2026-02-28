"""Run Montrixa Mini App API server (FastAPI)."""

import uvicorn

from config.settings import Settings


def main():
    uvicorn.run(
        "api.main:app",
        host=Settings.API_HOST,
        port=Settings.API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()

