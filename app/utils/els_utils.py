import json
import time
import urllib3

http = urllib3.PoolManager()

headers={'Accept': 'application/json', 'Content-type': 'application/json'}


def search(els_url, index, body, size = 10000):
    start = time.time()
    if not body:
        body = {
            "query": {"bool": {"must": []}},
        }
    body['size'] = size
    res = http.request('POST',f"http://{els_url}/{index}/_search", body=json.dumps(body), headers=headers)
    print(f"end {time.time()-start}")
    return json.loads(res.data)

if __name__ == "__main__":
    print(search("localhost:9200", "uservehicle", None, size=10000))