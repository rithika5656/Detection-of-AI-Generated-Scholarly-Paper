import os
import sys
# ensure src imports work when running from repo root
sys.path.insert(0, os.path.abspath('src'))

from web_app import app


def run_test():
    client = app.test_client()
    with open('data/sample_paper.txt', 'rb') as fh:
        data = {'file': (fh, 'sample_paper.txt')}
        rv = client.post('/analyze', data=data, content_type='multipart/form-data')
        print('Status:', rv.status_code)
        print('Response:')
        print(rv.get_data(as_text=True))

if __name__ == '__main__':
    run_test()
