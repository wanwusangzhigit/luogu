import requests
import json
import time
from bs4 import BeautifulSoup

# ============ 手动填写部分 ============
# 1. 题目编号（如 P1001）
PROBLEM_ID = "P1001"

# 2. 你的代码（注意转义）
CODE = '''#include<bits/stdc++.h>
using namespace std;
int main(){
    int a,b;
    cin>>a>>b;
    cout<<a+b;
    return 0;
}'''

# 3. 语言编号（28 = C++14 O2）
LANG = 28

# 4. 最新 Cookie（登录后复制完整字符串）
COOKIE = "__client_id=aaa; _uid=bbb; C3VK=ccc; gdxidpyhxdE=ddd"
# =====================================

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Cookie": COOKIE,
    "Referer": f"https://www.luogu.com.cn/problem/{PROBLEM_ID}",
    "Content-Type": "application/json"
})

def get_csrf_token():
    """获取 CSRF Token"""
    url = f"https://www.luogu.com.cn/problem/{PROBLEM_ID}"
    res = session.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    token = soup.find("meta", attrs={"name": "csrf-token"})
    if not token:
        raise Exception("CSRF Token 获取失败")
    return token["content"]

def submit_code():
    """提交代码到洛谷"""
    url = f"https://www.luogu.com.cn/fe/api/problem/submit/{PROBLEM_ID}"
    payload = {
        "lang": LANG,
        "code": CODE.strip(),
        "enableO2": 1
    }
    session.headers["X-CSRF-Token"] = get_csrf_token()
    resp = session.post(url, data=json.dumps(payload))
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == 200:
            return data["data"]["rid"]
    raise Exception(f"提交失败：{resp.status_code} {resp.text}")

def get_result(rid):
    """轮询获取评测结果"""
    url = f"https://www.luogu.com.cn/record/{rid}"
    while True:
        res = session.get(url)
        if "Accepted" in res.text:
            return "Accepted"
        if "评测中" not in res.text:
            # 提取最终状态
            soup = BeautifulSoup(res.text, "html.parser")
            status = soup.find("span", class_="status")
            return status.get_text(strip=True) if status else "未知状态"
        time.sleep(2)

if __name__ == "__main__":
    try:
        rid = submit_code()
        print("✅ 提交成功，记录 ID:", rid)
        result = get_result(rid)
        print("🎯 评测结果:", result)
    except Exception as e:
        print("❌ 错误:", e)