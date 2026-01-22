import os
import sys
import time
import subprocess

# Try TestClient first; if it fails (environment/version issues), fall back
# to starting a local Uvicorn process and posting via requests.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_with_testclient():
    from fastapi.testclient import TestClient
    from api import app
    client = TestClient(app)
    with open('data/sample_paper.txt', 'rb') as fh:
        files = {'file': ('sample_paper.txt', fh, 'text/plain')}
        rv = client.post('/analyze', files=files)
        print('Status:', rv.status_code)
        print(rv.text)


def run_with_uvicorn():
    import requests
    uv_cmd = [sys.executable, '-m', 'uvicorn', 'src.api:app', '--port', '8000']
    proc = subprocess.Popen(uv_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # wait briefly for server to start
        time.sleep(1.5)
        with open('data/sample_paper.txt', 'rb') as fh:
            files = {'file': ('sample_paper.txt', fh, 'text/plain')}
            rv = requests.post('http://127.0.0.1:8000/analyze', files=files, timeout=30)
            print('Status:', rv.status_code)
            print(rv.text)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == '__main__':
    try:
        run_with_testclient()
    except Exception as e:
        print('TestClient approach failed:', e)
        print('Falling back to starting uvicorn and using requests...')
        try:
            run_with_uvicorn()
        except Exception as e2:
            print('Uvicorn fallback also failed:', e2)
            print('Ensure dependencies are installed: pip install -r requirements.txt')
