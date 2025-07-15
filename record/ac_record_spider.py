# -*- coding: utf-8 -*-

import re
import json
import base64
import pathlib
import requests
import urllib.parse
pathlib.Path('ac').mkdir(exist_ok=True)
UID = "xxx"
COOKIES = {
    '__client_id': 'aaa',
    '_uid':UID,
    'C3VK': 'bbb',
}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
}

# 2. Luogu 语言编号 → 扩展名
LANG_EXT = {
    # C/C++
    1: 'c',      # C
    2: 'cpp',    # C++98/11
    28: 'cpp',   # C++17/20/23

    # 其他主流
    3: 'java',   # Java
    4: 'py',     # Python 3
    6: 'php',    # PHP
    7: 'js',     # JavaScript
    8: 'go',     # Go
    9: 'rs',     # Rust
    10: 'hs',    # Haskell
    11: 'pas',   # Pascal
    12: 'rb',    # Ruby
    14: 'scala', # Scala
    15: 'cs',    # C#
    16: 'kt',    # Kotlin
    17: 'swift', # Swift
    18: 'pl',    # Perl
    19: 'lua',   # Lua
    20: 'sh',    # Bash
    21: 'sql',   # SQL
    22: 'r',     # R
    23: 'm',     # Matlab / Octave
    24: 'pl6',   # Perl 6
    25: 'dart',  # Dart
    26: 'asm',   # Assembly
    27: 'f95',   # Fortran
    29: 'nim',   # Nim
    30: 'ml',    # OCaml / SML
    31: 'zig',   # Zig
    32: 'ts',    # TypeScript
    33: 'pas',   # FPC Pascal
    34: 'scm',   # Scheme
    35: 'clj',   # Clojure
    36: 'jl',    # Julia
    37: 'txt',   # 纯文本 / 其他
}

# 3. 通用：从 HTML 中提取 _feInjection JSON
def extract_fe(html: str) -> dict:
    m = re.search(r'window\._feInjection\s*=\s*JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', html, re.S)
    if not m:
        # 兜底：直接搜 JSON 块
        m = re.search(r'_feInjection\s*=\s*(\{.*?\});', html, re.S)
        if not m:
            raise RuntimeError('未找到 _feInjection JSON')
        return json.loads(m.group(1))
    return json.loads(urllib.parse.unquote(m.group(1)))

# 4. 会话
sess = requests.Session()
sess.headers.update(HEADERS)
sess.cookies.update(COOKIES)

# 5. 拉取主页面
all_records = []
per_page = 20  # Luogu 固定 20

page = 1
while True:
    url = f'https://www.luogu.com.cn/record/list?user=  '+UID+'&page={page}'
    html = sess.get(url, timeout=15).text
    fe = extract_fe(html)
    recs = fe['currentData']['records']['result']
    total = fe['currentData']['records']['count']

    all_records.extend(recs)

    # 已拉完所有页
    if page * per_page >= total:
        break
    page += 1

records = all_records
print(f'开始下载！')

# 6. 遍历并下载
for rec in records:
    # 只保留 AC 状态
    if rec.get('status') != 12:
        continue

    rid   = rec['id']
    pid   = rec['problem']['pid']
    lang  = rec['language']
    #  ext   = LANG_EXT.get(lang, 'txt')
    # 目前只支持 C++
    ext = "cpp"
    # 取详情页
    detail_html = sess.get(f'https://www.luogu.com.cn/record/  {rid}', timeout=15).text
    fe_detail   = extract_fe(detail_html)

    # 取源码
    raw_code = fe_detail.get('currentData', {}).get('record', {}).get('sourceCode')
    if not raw_code:
        print(f'⚠️ {pid} 无源码，跳过')
        continue
    source = raw_code.encode('utf-8').decode('unicode_escape')
    pathlib.Path('ac', f'{pid}.{ext}').write_text(source, encoding='utf-8')
    print(f'✅ AC {pid}.{ext} 已保存')
print('全部完成！')