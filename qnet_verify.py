import os,re,io,zipfile,subprocess,json,unicodedata,urllib.parse,requests,sys
from pathlib import Path
from pypdf import PdfReader

BASE=Path('qnet_verify'); BASE.mkdir(exist_ok=True)
PAGES={
2019:('5204672','https://www.q-net.or.kr/cst003.do?artlSeq=5204672&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2020:('5206735','https://www.q-net.or.kr/cst003.do?artlSeq=5206735&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2021:('5208224','https://www.q-net.or.kr/cst003.do?artlSeq=5208224&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2022:('5209468','https://www.q-net.or.kr/cst003.do?artlSeq=5209468&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2023:('5211560','https://www.q-net.or.kr/cst003.do?artlSeq=5211560&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2024:('5212808','https://www.q-net.or.kr/cst003.do?artlSeq=5212808&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2025:('5224724','https://www.q-net.or.kr/cst003.do?artlSeq=5224724&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
2026:('5251924','https://www.q-net.or.kr/cst003.do?artlSeq=5251924&boardId=Q004&gId=52&gSite=L&id=cst00302&menuType=cst00309'),
}
pat=re.compile(r"fileDown\('([^']+)',\s*'([^']+)',\s*'([^']+)'\)")

def dl_all():
 out={}
 for y,(art,u) in PAGES.items():
  html=requests.get(u,timeout=60).text
  ms=pat.findall(html)
  if not ms: raise RuntimeError(f'no attachments {y}')
  out[y]=[]
  for k,(path,name,seq) in enumerate(ms):
   url='https://www.q-net.or.kr/cst003.do?id=cst00302s01&gSite=L&gId=52&fileCode=R001&filePath='+urllib.parse.quote(path,safe='/')+'&fileName='+urllib.parse.quote_plus(name)+'&fileSeq='+seq+'&artlSeq='+art+'&href=0'
   r=requests.get(url,timeout=90); r.raise_for_status()
   safe=re.sub(r'[\\/:*?"<>|]','_',name)
   fn=BASE/f'{y}_{k}_{safe}'
   fn.write_bytes(r.content); out[y].append(fn)
 return out

def pdf_text(p):
 return '\n'.join((pg.extract_text() or '') for pg in PdfReader(str(p)).pages)

def hwp_text(p):
 outdir=BASE/'lo'; outdir.mkdir(exist_ok=True)
 subprocess.run(['libreoffice','--headless','--convert-to','pdf','--outdir',str(outdir),str(p)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 pdf=outdir/(p.stem+'.pdf')
 if not pdf.exists(): raise RuntimeError(f'LibreOffice conversion failed: {p}')
 return pdf_text(pdf)

def collect_year(y,files):
 texts=[]
 for f in files:
  low=f.name.lower()
  if low.endswith('.zip'):
   zdir=BASE/f'z{y}'; zdir.mkdir(exist_ok=True)
   with zipfile.ZipFile(f) as z: z.extractall(zdir)
   cand=[p for p in zdir.rglob('*') if p.is_file() and p.suffix.lower() in ('.pdf','.hwp')]
   a=[p for p in cand if ('a형' in p.name.lower() or ' a' in p.name.lower())]
   if a: cand=a
   for p in cand:
    try: texts.append(pdf_text(p) if p.suffix.lower()=='.pdf' else hwp_text(p))
    except Exception as e: print('EXTRACT_FAIL',p,e)
  elif low.endswith('.pdf'): texts.append(pdf_text(f))
  elif low.endswith('.hwp'): texts.append(hwp_text(f))
 return '\n'.join(texts)

def norm(s):
 s=unicodedata.normalize('NFKC',str(s)).replace('ㆍ','·').replace('․','·')
 s=re.sub(r'\s+','',s)
 s=re.sub(r'[\u00ad\ufeff\u200b]','',s)
 return s

exams=requests.get('https://raw.githubusercontent.com/effect082/examone/main/data/exam_data.json',timeout=60).json()
byid={e.get('id'):e for e in exams}
files=dl_all()
official={y:collect_year(y,files[y]) for y in PAGES}
for y,t in official.items(): (BASE/f'official_{y}.txt').write_text(t,'utf-8')

rows=[]
for y in range(2019,2027):
 no=norm(official[y])
 for sess in (1,2,3):
  e=byid[f's{y}-{sess}']
  for q in e.get('questions',[]):
   qn=int(q.get('qnum') or 0); qt=str(q.get('question') or '').strip(); ops=q.get('options') or []
   if not qt: status='BROKEN_EMPTY'
   elif len(ops)!=5: status='BROKEN_OPTIONS'
   else: status='MATCH' if norm(qt) in no else 'MISMATCH'
   rows.append({'year':y,'session':sess,'qnum':qn,'status':status,'question':qt,'options_count':len(ops)})

from collections import Counter
c=Counter(r['status'] for r in rows)
Path('qnet_verify_summary.txt').write_text('\n'.join([f'{k}: {v}' for k,v in sorted(c.items())]+[f'TOTAL: {len(rows)}']),'utf-8')
Path('qnet_verify_report.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
print(Path('qnet_verify_summary.txt').read_text())
for r in rows:
 if r['status']!='MATCH': print(r['year'],r['session'],r['qnum'],r['status'],r['question'][:120])
