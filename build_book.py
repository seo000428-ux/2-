import json, random, re
import requests
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from pypdf import PdfReader

URL='https://raw.githubusercontent.com/effect082/examone/main/data/exam_data.json'
r=requests.get(URL,timeout=60); r.raise_for_status(); exams=r.json()
years=range(2019,2027)
rounds={2019:17,2020:18,2021:19,2022:20,2023:21,2024:22,2025:23,2026:24}
subjects=[('인간행동과 사회환경',1,1,25),('사회복지조사론',1,26,50),('사회복지실천론',2,1,25),('사회복지실천기술론',2,26,50),('지역사회복지론',2,51,75),('사회복지정책론',3,1,25),('사회복지행정론',3,26,50),('사회복지법제론',3,51,75)]
expected={1:50,2:75,3:75}; byid={e.get('id'):e for e in exams}; all_items={x[0]:[] for x in subjects}; audit=[]
for y in years:
  for sess in (1,2,3):
    e=byid.get(f's{y}-{sess}')
    if not e: raise RuntimeError(f'Missing s{y}-{sess}')
    raw=e.get('questions',[]); valid=[q for q in raw if len(q.get('options') or [])==5 and str(q.get('question','')).strip()]
    if len(valid)!=expected[sess]: raise RuntimeError(f's{y}-{sess}: expected {expected[sess]} valid, got {len(valid)} raw={len(raw)}')
    sr=sorted(raw,key=lambda q:int(q.get('qnum') or 0))
    ans=[str(q.get('correct_answer','')).strip() for q in sr if str(q.get('correct_answer','')).strip() in {'1','2','3','4','5'}][:expected[sess]]
    if len(ans)!=expected[sess]: ans=[str(q.get('correct_answer','')).strip() for q in valid]
    if len(ans)!=expected[sess] or any(a not in '12345' for a in ans): raise RuntimeError(f'bad answers s{y}-{sess}: {len(ans)}')
    for i,q in enumerate(valid,1):
      subj=next(n for n,ss,a,b in subjects if ss==sess and a<=i<=b)
      all_items[subj].append({'year':y,'round':rounds[y],'session':sess,'orig_q':i,'question':re.sub(r'\s+',' ',str(q.get('question','')).strip()),'options':[re.sub(r'\s+',' ',str(o).strip()) for o in q.get('options',[])],'answer':ans[i-1]})
    audit.append((y,sess,len(raw),len(valid)))
for name,v in all_items.items():
  if len(v)!=200: raise RuntimeError(f'{name}: {len(v)}')
  random.Random('sw1-2019-2026-'+name).shuffle(v)

font='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'; bold='/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'
pdfmetrics.registerFont(TTFont('NG',font)); pdfmetrics.registerFont(TTFont('NGB',bold))
PW,PH=A4
def footer(c,d):
  c.saveState(); c.setFont('NG',8); c.setFillColor(colors.HexColor('#666666')); c.drawRightString(PW-15*mm,9*mm,str(d.page)); c.restoreState()
cover=ParagraphStyle('cover',fontName='NGB',fontSize=25,leading=35,alignment=TA_CENTER,spaceAfter=8*mm)
cover2=ParagraphStyle('cover2',fontName='NG',fontSize=13,leading=20,alignment=TA_CENTER,textColor=colors.HexColor('#444444'))
chap=ParagraphStyle('chap',fontName='NGB',fontSize=20,leading=28,spaceAfter=5*mm)
qstyle=ParagraphStyle('q',fontName='NGB',fontSize=10.2,leading=16,spaceAfter=1.8*mm,wordWrap='CJK')
srcstyle=ParagraphStyle('src',fontName='NG',fontSize=7.5,leading=9,alignment=TA_RIGHT,textColor=colors.HexColor('#777777'))
optstyle=ParagraphStyle('opt',fontName='NG',fontSize=9.4,leading=14,spaceAfter=0.5*mm,wordWrap='CJK')
note=ParagraphStyle('note',fontName='NG',fontSize=9,leading=15,textColor=colors.HexColor('#555555'),wordWrap='CJK')
ansstyle=ParagraphStyle('ans',fontName='NG',fontSize=8.5,leading=11,wordWrap='CJK')
anshead=ParagraphStyle('anshead',fontName='NGB',fontSize=18,leading=24,spaceAfter=4*mm)
problem='사회복지사1급_기출문제집_2019-2026_1600문항.pdf'
story=[Spacer(1,42*mm),Paragraph('사회복지사 1급<br/>기출문제집',cover),Paragraph('2019–2026 · 8개 영역 × 200문항 · 총 1,600문항',cover2),Spacer(1,18*mm),Paragraph('연도별 문제를 과목 안에서 섞어 구성했으며, 각 문항에 원문 출처(연도/회차/교시/문항)를 표시했습니다.',note),Spacer(1,4*mm),Paragraph('※ 공개 기출 전산화 자료 기반으로 일부 띄어쓰기·수식·특수기호가 원문과 다르게 보일 수 있습니다.<br/>※ 사회복지법제론은 해당 시험 시행일 당시 법령 기준이며 현행 법령과 다를 수 있습니다.',note),PageBreak()]
for si,(name,_,_,_) in enumerate(subjects,1):
  story += [Paragraph(f'{si}. {name}',chap),Paragraph('2019~2026 기출 200문항 · 연도 혼합',note),Spacer(1,4*mm)]
  for n,it in enumerate(all_items[name],1):
    tag=f"[{it['year']}/#{it['round']}/S{it['session']}-Q{it['orig_q']}]"
    block=[Paragraph(tag,srcstyle),Paragraph(f'{n}. {it["question"]}',qstyle)]+[Paragraph(o,optstyle) for o in it['options']]+[Spacer(1,3*mm)]
    story.append(KeepTogether(block))
  if si<len(subjects): story.append(PageBreak())
SimpleDocTemplate(problem,pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=14*mm,bottomMargin=15*mm,title='사회복지사 1급 기출문제집 2019-2026').build(story,onFirstPage=footer,onLaterPages=footer)

answer='사회복지사1급_기출문제집_2019-2026_답지.pdf'
astory=[Spacer(1,25*mm),Paragraph('사회복지사 1급 기출문제집<br/>정답표',cover),Paragraph('2019–2026 · 총 1,600문항',cover2),Spacer(1,15*mm),Paragraph('※ 정답은 전산화 기출 자료의 답안표를 기준으로 재구성했습니다. 사회복지법제론은 시험 당시 법령 기준입니다.',note),PageBreak()]
for si,(name,_,_,_) in enumerate(subjects,1):
  astory.append(Paragraph(f'{si}. {name}',anshead)); rows=[[Paragraph('<b>번호</b>',ansstyle),Paragraph('<b>정답</b>',ansstyle),Paragraph('<b>출처</b>',ansstyle),Paragraph('<b>번호</b>',ansstyle),Paragraph('<b>정답</b>',ansstyle),Paragraph('<b>출처</b>',ansstyle)]]; items=all_items[name]
  for i in range(100):
    row=[]
    for idx in (i,i+100):
      it=items[idx]; row += [Paragraph(str(idx+1),ansstyle),Paragraph(it['answer'],ansstyle),Paragraph(f"{it['year']}/#{it['round']}/S{it['session']}-Q{it['orig_q']}",ansstyle)]
    rows.append(row)
  t=Table(rows,colWidths=[11*mm,11*mm,41*mm,11*mm,11*mm,41*mm],repeatRows=1,hAlign='LEFT'); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#BBBBBB')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEEEEE')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(1,-1),'CENTER'),('ALIGN',(3,0),(4,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),2.2),('BOTTOMPADDING',(0,0),(-1,-1),2.2)])); astory.append(t)
  if si<len(subjects): astory.append(PageBreak())
SimpleDocTemplate(answer,pagesize=A4,rightMargin=12*mm,leftMargin=12*mm,topMargin=13*mm,bottomMargin=14*mm,title='사회복지사 1급 기출문제집 답지 2019-2026').build(astory,onFirstPage=footer,onLaterPages=footer)
with open('검증결과.txt','w',encoding='utf-8') as f:
  f.write('사회복지사 1급 2019-2026 기출문제집 검증\n'); f.write(f'총 문항: {sum(map(len,all_items.values()))}\n')
  for name in all_items:f.write(f'{name}: {len(all_items[name])}\n')
  f.write('\n세션 필터 검증(raw -> 실제문항)\n')
  for y,s,rw,v in audit:f.write(f'{y} S{s}: {rw} -> {v}\n')
  f.write(f'문제집 페이지: {len(PdfReader(problem).pages)}\n답지 페이지: {len(PdfReader(answer).pages)}\n')
print(open('검증결과.txt',encoding='utf-8').read())