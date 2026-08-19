import requests,re
from bs4 import BeautifulSoup
u='https://www.q-net.or.kr/cst003.do?artlSeq=5204672&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'
r=requests.get(u,timeout=30); print('STATUS',r.status_code,'URL',r.url,'LEN',len(r.text))
print('ENC',r.encoding)
s=BeautifulSoup(r.text,'html.parser')
for a in s.find_all('a'):
    text=' '.join(a.stripped_strings)
    href=a.get('href','')
    onclick=a.get('onclick','')
    if 'zip' in text.lower() or '다운' in text or 'file' in href.lower() or 'down' in href.lower() or 'atch' in href.lower() or 'file' in onclick.lower() or 'down' in onclick.lower():
        print('A',repr(text),repr(href),repr(onclick))
for m in re.findall(r'.{0,180}(?:zip|atch|download|file).{0,260}',r.text,re.I): print('RAW',m[:500])