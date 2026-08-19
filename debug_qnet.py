import requests
URL='https://raw.githubusercontent.com/effect082/examone/main/data/exam_data.json'
exams=requests.get(URL,timeout=60).json()
byid={e.get('id'):e for e in exams}
for y in range(2019,2027):
  for s in (1,2,3):
    e=byid[f's{y}-{s}']
    bad=[]
    for q in e.get('questions',[]):
      opts=q.get('options') or []
      text=(q.get('question') or '').strip()
      if len(opts)!=5 or not text:
        bad.append((q.get('qnum'),len(opts),repr(text[:160]),[repr(str(x)[:120]) for x in opts]))
    print(f's{y}-{s} raw={len(e.get("questions",[]))} bad={len(bad)}')
    for x in bad: print('BAD',x)
