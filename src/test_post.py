import sys
import os

# Make sure repo root is on path so src modules import correctly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

import web_app

client = web_app.app.test_client()
path = os.path.join(ROOT, 'data', 'uploads', 'sample_paper.txt')
with open(path, 'rb') as f:
    data = {'file': (f, 'sample_paper.txt')}
    resp = client.post('/analyze', data=data, content_type='multipart/form-data')
    print(resp.get_data(as_text=True))
