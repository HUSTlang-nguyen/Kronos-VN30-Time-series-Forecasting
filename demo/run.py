"""One-process local server, optionally opening the user's browser when ready."""
import argparse
import threading
import time
import urllib.request
import webbrowser
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()
    if args.cpu:
        os.environ["VN30_DEVICE"] = "cpu"
    address = f"http://127.0.0.1:{args.port}"
    if args.open_browser:
        def open_when_ready():
            for _ in range(80):
                try:
                    with urllib.request.urlopen(address + "/api/health", timeout=2):
                        webbrowser.open(address)
                        return
                except Exception:
                    time.sleep(0.5)
        threading.Thread(target=open_when_ready, daemon=True).start()
    import uvicorn
    print("VN30 Inference Studio: " + address)
    uvicorn.run("demo.app:create_app", factory=True, host="127.0.0.1", port=args.port, workers=1)


if __name__ == "__main__":
    main()
