import requests,zipfile,io,os,re
from urllib.parse import urlencode
from pypdf import PdfReader
base='https://www.q-net.or.kr/cst003.do'
params={'id':'cst00302s01','gSite':'L','gId':'52','fileCode':'R001','filePath':'bbs/Q004/Q004_2189307','fileName':'Q-Net 시험문제지 등재(2019년도 제17회 사회복지사 1급).zip','fileSeq':'2189307','artlSeq':'5204672','href':'0'}
r=requests.get(base,params=params,timeout=60); print('ZIP',r.status_code,r.url,r.headers.get('content-type'),len(r.content)); r.raise_for_status()
z=zipfile.ZipFile(io.BytesIO(r.content)); print('FILES'); [print(repr(n)) for n in z.namelist()]
for n in z.namelist():
    low=n.lower()
    if low.endswith('.pdf') and ('a형' in n.lower() or 'a.' in low or '_a' in low or ' a' in low):
        try:
            rd=PdfReader(io.BytesIO(z.read(n)))
            print('\n=====PDF',repr(n),'PAGES',len(rd.pages),'=====')
            for i,p in enumerate(rd.pages[:5]):
                txt=p.extract_text() or ''
                print(f'---PAGE {i+1}---')
                print(txt[:12000])
        except Exception as e: print('ERR',n,e)