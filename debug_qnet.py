import requests,re,io,urllib.parse
from pypdf import PdfReader
page='https://www.q-net.or.kr/cst003.do?artlSeq=5224724&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'
s=requests.Session(); t=s.get(page,timeout=30).text
pat=r"fileDown\('([^']+)',\s*'([^']+)',\s*'([^']+)'\)"
ms=re.findall(pat,t)
print('FILES',ms)
for path,name,seq in ms:
 if '1교시' not in name: continue
 u='https://www.q-net.or.kr/cst003.do?id=cst00302s01&gSite=L&gId=52&fileCode=R001&filePath='+urllib.parse.quote(path,safe='/')+'&fileName='+urllib.parse.quote_plus(name)+'&fileSeq='+seq+'&artlSeq=5224724&href=0'
 r=s.get(u,timeout=60); print('DL',r.status_code,len(r.content),r.headers.get('content-type'))
 rd=PdfReader(io.BytesIO(r.content))
 for i,p in enumerate(rd.pages):
  txt=p.extract_text() or ''
  if '33.' in txt or '취약청소년' in txt:
   print('PAGE',i+1); print(txt)
