#!/usr/bin/env python3
"""Local development server."""

from web.app_core import app


def main():
    import uvicorn

    print("G05 STLF — http://127.0.0.1:8000")
    print("API docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
