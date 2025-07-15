import requests

BASE = "https://www.luogu.com.cn/"
sess = requests.Session()
sess.headers.update({"User-Agent": "Python-luogu-api-demo"})

def get_problem(pid: str):
    url = f"{BASE}problem/{pid}.json"
    r = sess.get(url, timeout=10)
    r.raise_for_status()
    return r.json()["currentData"]["problem"]

if __name__ == "__main__":
    print(get_problem("P1000")["title"])