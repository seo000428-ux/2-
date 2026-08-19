import json, random, re
from xml.sax.saxutils import escape
import requests
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from pypdf import PdfReader

URL='https://raw.githubusercontent.com/effect082/examone/main/data/exam_data.json'
YEARS=range(2019,2027)
ROUNDS={2019:17,2020:18,2021:19,2022:20,2023:21,2024:22,2025:23,2026:24}
SUBJECTS=[
 ('인간행동과 사회환경',1,1,25),('사회복지조사론',1,26,50),
 ('사회복지실천론',2,1,25),('사회복지실천기술론',2,26,50),('지역사회복지론',2,51,75),
 ('사회복지정책론',3,1,25),('사회복지행정론',3,26,50),('사회복지법제론',3,51,75)
]
EXPECTED={1:50,2:75,3:75}

# Q-Net 2019 제17회 A형 원문에서 복원한, 전산화 데이터에 누락된 각 교시 1~6번.
MISSING_2019={
1:[
 {'question':'인간행동과성격에관한설명으로옳지않은것은?','options':['① 인간행동은개인의성격특성에따라다르게표출된다.','② 성격을이해하면행동의변화추이를예측할수있다.','③ 인간행동의이해와개입을위해서는성격의이해가필요하다.','④ 성격이론은인간행동의수정방법을찾는데도움이된다.','⑤ 성격은심리역동적특성이있어일관된행동을기대할수없다.']},
 {'question':'인간발달이론이사회복지실천에유용한이유로옳지않은것은?','options':['① 개인적응과부적응의판단기준이된다.','② 모든연령계층의클라이언트와일할수있는기반이된다.','③ 생애주기에따른변화와안정요인을이해하게한다.','④ 발달단계에따라신체,심리,사회적기능을분절적으로이해하게한다.','⑤ 발달단계별욕구에따른사회복지제도의기반을제공한다.']},
 {'question':'인간발달의원리로옳지않은것은?','options':['① 유전과환경의영향을모두받는다.','② 일생에걸친예측불가능한변화이다.','③ 발달의정도와속도는개인마다다르다.','④ 일정한순서와방향성이존재한다.','⑤ 멈추는일없이지속된다.']},
 {'question':'에릭슨(E. Erikson)의심리사회적발달단계에서긍정적결과와주요관계의연결이옳지않은것은?','options':['① 영아기(0-2세,신뢰감대불신감):지혜-어머니','② 유아기(2-4세,자율성대수치심과의심):의지-부모','③ 학령전기(4-6세,주도성대죄의식):목적-가족','④ 아동기(6-12세,근면성대열등감):능력-이웃,학교','⑤ 청소년기(12-19세,자아정체감대정체감혼란):성실-또래집단']},
 {'question':'프로이드(S. Freud)의정신분석이론에서불안에관한설명으로옳은것을모두고른것은? ㄱ. 불안: 공포상태로서위급한상황에적합한방법으로반응하지못하는것이다. ㄴ. 현실적불안: 자아가지각한현실세계에있는위협상황에대한두려움이다. ㄷ. 신경증적불안: 원초아의충동이의식될지도모른다는위협을느낄때생기는두려움이다. ㄹ. 도덕적불안: 원초아와초자아간의갈등에서느끼는양심에대한두려움이다.','options':['① ㄱ, ㄷ','② ㄴ, ㄹ','③ ㄱ, ㄴ, ㄷ','④ ㄴ, ㄷ, ㄹ','⑤ ㄱ, ㄴ, ㄷ, ㄹ']},
 {'question':'방어기제에관한설명으로옳지않은것은?','options':['① 반동형성(reaction formation): 어떤충동이나감정을반대로표현하는것이다.','② 전치(displacement): 본능적충동의대상을원래의대상에서덜위협적인대상으로옮겨서발산하는것이다.','③ 전환(conversion): 심리적갈등이감각기관또는수의근계기관의증상으로표출되는것이다.','④ 투사(projection): 용납할수없는자신의충동,생각,행동을무의식적으로다른사람의탓으로돌리는것이다.','⑤ 해리(dissociation): 어떤대상에피해를주었을경우,취소또는무효화하는것이다.']}
],
2:[
 {'question':'사회복지실천의목적과기능으로옳지않은것은?','options':['① 사회정의의증진','② 클라이언트의삶의질증진','③ 클라이언트의가능성과잠재력개발','④ 개인과사회간상호유익한관계증진','⑤ 개인이조직에게효과적으로순응하도록원조']},
 {'question':'이용시설-간접서비스기관-민간기관의예를순서대로바르게나열한것은?','options':['① 지역아동센터-사회복지협의회-주민센터','② 장애인복지관-주민센터-지역사회보장협의체','③ 청소년쉼터-사회복지관-사회복지공동모금회','④ 사회복지관-노인보호전문기관-성폭력피해상담소','⑤ 다문화가족지원센터-사회복지공동모금회-한국사회복지사협회']},
 {'question':'사회복지전문직에관한설명으로옳은것을모두고른것은? ㄱ. 전문적인이론체계를갖고있음 ㄴ. 개인의변화와사회적변혁에관심을둠 ㄷ. 미시및거시적개입방법을모두이해해야함 ㄹ. 타분야전문가와의협업을위해고유한정체성의발전은불필요함','options':['① ㄱ, ㄴ','② ㄱ, ㄷ','③ ㄴ, ㄷ','④ ㄱ, ㄴ, ㄷ','⑤ ㄱ, ㄷ, ㄹ']},
 {'question':'사회복지사의가치갈등이나윤리적딜레마에관한설명으로옳지않은것은?','options':['① 윤리기준은지속적으로변화된다.','② 가치갈등에대응하는첫단계는가치갈등의존재를인식하는것이다.','③ 윤리적결정에따른결과의모호성으로윤리적딜레마가발생할수있다.','④ 기관의목표가클라이언트이익에위배될때가치상충으로윤리적딜레마가발생할수있다.','⑤ 윤리적결정을위해로웬버그와돌고프(F. Loewenberg & R. Dolgoff)의일반결정모델을활용할수있다.']},
 {'question':'사회복지사윤리에관한설명으로옳은것을모두고른것은? ㄱ. 사회복지사는원조과정에서자신의이익을위해행동해서는안됨 ㄴ. 로웬버그와돌고프의윤리원칙준거틀은생명보호를최우선으로함 ㄷ. 윤리강령은윤리적갈등이생겼을때법적제재의근거를제공함 ㄹ. 사회복지사는국가자격이므로사회복지사윤리강령은국가가채택함','options':['① ㄱ, ㄴ','② ㄱ, ㄷ','③ ㄱ, ㄴ, ㄷ','④ ㄱ, ㄴ, ㄹ','⑤ ㄴ, ㄷ, ㄹ']},
 {'question':'사회복지사의역할에관한설명으로옳지않은것은?','options':['① 옹호자: 클라이언트권익변호','② 계획자: 변화과정기획','③ 연구자: 개입효과평가','④ 교육자: 지식과기술전수','⑤ 중개자: 조직이나집단의갈등해결']}
],
3:[
 {'question':'우리나라사회보장제도운영주체의책임에관한원칙으로옳은것은?','options':['① 사회보험은국가의책임으로시행한다.','② 공공부조는지방자치단체가전적으로책임지고시행한다.','③ 사회서비스는지방자치단체만의책임으로시행한다.','④ 국가는사회보장에관하여민간단체의참여를제한한다.','⑤ 사회보험에드는비용은국가가전담한다.']},
 {'question':'우리나라사회복지제도중에서보편주의범주에포함되는것은?','options':['① 의료급여','② 생계급여','③ 주거급여','④ 실업급여','⑤ 기초연금']},
 {'question':'민간의사회복지에대한우리나라사회복지정책의내용이아닌것은?','options':['① 국가와지방자치단체는국가및지방자치단체의사회복지사업과민간부문의사회복지증진활동이원활하게연계될수있도록노력하여야한다.','② 국가와지방자치단체는사회복지를필요로하는사람의인권이충분히존중되는방식으로사회복지서비스를제공하여야한다.','③ 보건복지부장관은사회복지시설에서제공하는사회복지서비스의최저기준을마련하여야한다.','④ 국가나지방자치단체가설치한사회복지시설은사회복지법인이나비영리법인에위탁하여운영하게할수있다.','⑤ 국가나지방자치단체는사회복지법인에우선하여사회복지시설을설치ㆍ운영할수없다.']},
 {'question':'반집합주의가선호하는가치영역이아닌것은?','options':['① 개인','② 시장','③ 평등','④ 가족','⑤ 경쟁']},
 {'question':'우리나라산업재해보상보험제도에서업무상재해의인정기준을모두고른것은? ㄱ. 출퇴근재해 ㄴ. 업무상질병 ㄷ. 업무상사고 ㄹ. 장애등급','options':['① ㄴ, ㄹ','② ㄱ, ㄴ, ㄷ','③ ㄱ, ㄷ, ㄹ','④ ㄴ, ㄷ, ㄹ','⑤ ㄱ, ㄴ, ㄷ, ㄹ']},
 {'question':'평등에관한설명으로옳지않은것은?','options':['① 보험료수준에따라급여를차등하는것은비례적평등으로볼수있다.','② 드림스타트(Dream Start)사업은기회의평등을반영하는것으로볼수있다.','③ 공공부조의급여는산술적평등을,열등처우의원칙은비례적평등을반영하는것이다.','④ 모든사람에게동등한의료서비스를제공하는영국의국민보건서비스(NHS)는결과의평등을반영하는것으로볼수있다.','⑤ 비례적평등은결과의평등이다.']}
]
}

def clean(s): return re.sub(r'\s+',' ',str(s or '').strip())
def safe(s): return escape(str(s))

r=requests.get(URL,timeout=60); r.raise_for_status(); exams=r.json(); byid={e.get('id'):e for e in exams}
all_items={x[0]:[] for x in SUBJECTS}; audit=[]
for y in YEARS:
  for sess in (1,2,3):
    e=byid.get(f's{y}-{sess}')
    if not e: raise RuntimeError(f'Missing s{y}-{sess}')
    raw=e.get('questions',[]); sr=sorted(raw,key=lambda q:int(q.get('qnum') or 0))
    answer_seq=[str(q.get('correct_answer','')).strip() for q in sr]
    if len(answer_seq)!=EXPECTED[sess] or any(a not in {'1','2','3','4','5'} for a in answer_seq):
      raise RuntimeError(f's{y}-{sess}: invalid answer sequence len={len(answer_seq)}')
    valid=[{'question':clean(q.get('question')),'options':[clean(o) for o in q.get('options',[])]} for q in sr if len(q.get('options') or [])==5 and clean(q.get('question'))]
    if y==2019:
      if len(valid)!=EXPECTED[sess]-6: raise RuntimeError(f's2019-{sess}: expected {EXPECTED[sess]-6} surviving questions, got {len(valid)}')
      restored=[{'question':clean(q['question']),'options':[clean(o) for o in q['options']]} for q in MISSING_2019[sess]]+valid
    else:
      if len(valid)!=EXPECTED[sess]: raise RuntimeError(f's{y}-{sess}: expected {EXPECTED[sess]} valid, got {len(valid)} raw={len(raw)}')
      restored=valid
    if len(restored)!=EXPECTED[sess]: raise RuntimeError(f's{y}-{sess}: restored len={len(restored)}')
    for i,q in enumerate(restored,1):
      subj=next(n for n,ss,a,b in SUBJECTS if ss==sess and a<=i<=b)
      all_items[subj].append({'year':y,'round':ROUNDS[y],'session':sess,'orig_q':i,'question':q['question'],'options':q['options'],'answer':answer_seq[i-1]})
    audit.append((y,sess,len(raw),len(valid),len(restored)))

for name,v in all_items.items():
  if len(v)!=200: raise RuntimeError(f'{name}: expected 200 got {len(v)}')
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
story=[Spacer(1,42*mm),Paragraph('사회복지사 1급<br/>기출문제집',cover),Paragraph('2019–2026 · 8개 영역 × 200문항 · 총 1,600문항',cover2),Spacer(1,18*mm),Paragraph('연도별 문제를 과목 안에서 섞어 구성했으며, 각 문항에 원문 출처(연도/회차/교시/문항)를 표시했습니다.',note),Spacer(1,4*mm),Paragraph('※ 공개 기출 전산화 자료를 기본으로 하되 2019년 전산화 누락 18문항은 Q-Net 제17회 A형 원문에서 복원했습니다.<br/>※ 전산화 과정에서 일부 띄어쓰기·수식·특수기호 표현이 원문과 다르게 보일 수 있습니다.<br/>※ 사회복지법제론은 해당 시험 시행일 당시 법령 기준이며 현행 법령과 다를 수 있습니다.',note),PageBreak()]
for si,(name,_,_,_) in enumerate(SUBJECTS,1):
  story += [Paragraph(f'{si}. {safe(name)}',chap),Paragraph('2019~2026 기출 200문항 · 연도 혼합',note),Spacer(1,4*mm)]
  for n,it in enumerate(all_items[name],1):
    tag=f"[{it['year']}/#{it['round']}/S{it['session']}-Q{it['orig_q']}]"
    block=[Paragraph(safe(tag),srcstyle),Paragraph(f'{n}. {safe(it["question"])}',qstyle)]
    block += [Paragraph(safe(o),optstyle) for o in it['options']]
    block += [Spacer(1,3*mm)]
    story.append(KeepTogether(block))
  if si<len(SUBJECTS): story.append(PageBreak())
SimpleDocTemplate(problem,pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=14*mm,bottomMargin=15*mm,title='사회복지사 1급 기출문제집 2019-2026').build(story,onFirstPage=footer,onLaterPages=footer)

answer='사회복지사1급_기출문제집_2019-2026_답지.pdf'
astory=[Spacer(1,25*mm),Paragraph('사회복지사 1급 기출문제집<br/>정답표',cover),Paragraph('2019–2026 · 총 1,600문항',cover2),Spacer(1,15*mm),Paragraph('※ 정답은 기출 답안표 기준입니다. 사회복지법제론은 시험 당시 법령 기준입니다.',note),PageBreak()]
for si,(name,_,_,_) in enumerate(SUBJECTS,1):
  astory.append(Paragraph(f'{si}. {safe(name)}',anshead)); items=all_items[name]
  rows=[[Paragraph('<b>번호</b>',ansstyle),Paragraph('<b>정답</b>',ansstyle),Paragraph('<b>출처</b>',ansstyle),Paragraph('<b>번호</b>',ansstyle),Paragraph('<b>정답</b>',ansstyle),Paragraph('<b>출처</b>',ansstyle)]]
  for i in range(100):
    row=[]
    for idx in (i,i+100):
      it=items[idx]; tag=f"{it['year']}/#{it['round']}/S{it['session']}-Q{it['orig_q']}"
      row += [Paragraph(str(idx+1),ansstyle),Paragraph(it['answer'],ansstyle),Paragraph(safe(tag),ansstyle)]
    rows.append(row)
  t=Table(rows,colWidths=[11*mm,11*mm,41*mm,11*mm,11*mm,41*mm],repeatRows=1,hAlign='LEFT')
  t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#BBBBBB')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEEEEE')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(1,-1),'CENTER'),('ALIGN',(3,0),(4,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),2.2),('BOTTOMPADDING',(0,0),(-1,-1),2.2)])); astory.append(t)
  if si<len(SUBJECTS): astory.append(PageBreak())
SimpleDocTemplate(answer,pagesize=A4,rightMargin=12*mm,leftMargin=12*mm,topMargin=13*mm,bottomMargin=14*mm,title='사회복지사 1급 기출문제집 답지 2019-2026').build(astory,onFirstPage=footer,onLaterPages=footer)

with open('검증결과.txt','w',encoding='utf-8') as f:
  f.write('사회복지사 1급 2019-2026 기출문제집 검증\n')
  f.write(f'총 문항: {sum(map(len,all_items.values()))}\n')
  for name in all_items: f.write(f'{name}: {len(all_items[name])}\n')
  f.write('\n세션 검증(raw / 5지선다 실문항 / 복원 후)\n')
  for y,s,rw,v,rs in audit: f.write(f'{y} S{s}: {rw} / {v} / {rs}\n')
  f.write(f'문제집 페이지: {len(PdfReader(problem).pages)}\n')
  f.write(f'답지 페이지: {len(PdfReader(answer).pages)}\n')
print(open('검증결과.txt',encoding='utf-8').read())