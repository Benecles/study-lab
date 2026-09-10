#!/usr/bin/env python3
"""Render the source-mapped authored unit 08. Run after build_course.py."""
from pathlib import Path
import html,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tools/editorial/unit08.json'
OUT=ROOT/'courses/teoria-do-delito/unidade-08.html'
def esc(s):return html.escape(str(s))
def paras(s):return ''.join('<p>'+esc(p.strip())+'</p>' for p in s.split('\n\n') if p.strip())
def items_dl(items):return '<dl>'+''.join('<div class="comparison-row"><dt>'+esc(i['label'])+'</dt><dd>'+paras(i['text'])+'</dd></div>' for i in items)+'</dl>'
def render_block(b):
 t=b['type'];title=b.get('title','');txt=b.get('text','');items=b.get('items',[])
 if title=='Fases e perguntas jurídicas':
  return '<div class="timeline full-width"><ol>'+''.join('<li><h3>'+esc(i['label'])+'</h3>'+paras(i['text'])+'</li>' for i in items)+'</ol><p class="timeline-note">O início da execução precisa ser demonstrado no caso concreto.</p></div>'
 if title=='Elementos que precisam ser demonstrados':
  return '<div class="requirements full-width"><h3>Art. 14, II</h3><ol>'+''.join('<li><span class="req-number" aria-hidden="true">'+str(n+1)+'</span><h4>'+esc(i['label'])+'</h4>'+paras(i['text'])+'</li>' for n,i in enumerate(items))+'</ol><p class="legal-margin">Os três requisitos precisam estar presentes.</p></div>'
 if title=='Absoluto e contingente':
  return '<div class="impossibility full-width"><div class="absolute"><h3>Impossibilidade absoluta</h3>'+''.join('<h4>'+esc(i['label'])+'</h4>'+paras(i['text']) for i in items[:2])+'</div><div class="contingent"><h3>Falha contingente</h3>'+paras(items[2]['text'])+'<aside><h4>'+esc(items[3]['label'])+'</h4>'+paras(items[3]['text'])+'</aside></div></div>'
 if title=='Critérios em confronto':
  return '<div class="criteria-map full-width"><h3>Este ato já é execução?</h3>'+paras(txt)+'<div class="criteria-branches">'+''.join('<article><h4>'+esc(i['label'])+'</h4>'+paras(i['text'])+'</article>' for i in items)+'</div></div>'
 if title=='Prova: fato favorável e cautela':
  rows=''
  for i in items:
   yes,no=i['text'].split('; cautela: ',1)
   rows+='<div class="evidence-row"><h4>'+esc(i['label'])+'</h4><p><span class="sr-only">Indício: </span>'+esc(yes)+'.</p><p><span class="sr-only">Cautela: </span>'+esc(no[0].upper()+no[1:])+'</p></div>'
  return '<div class="evidence full-width"><h3>'+esc(title)+'</h3>'+paras(txt)+'<div class="evidence-head" aria-hidden="true"><span>Hipótese</span><span>Indício</span><span>Verifique também</span></div>'+rows+'</div>'
 if t=='comparison':return '<div class="comparison"><h3>'+esc(title)+'</h3>'+paras(txt)+items_dl(items)+'</div>'
 if t=='prose':return '<div class="prose-block"><h3>'+esc(title)+'</h3>'+paras(txt)+'</div>'
 if t=='note':return '<aside class="section-note"><h3>'+esc(title)+'</h3>'+paras(txt)+'</aside>'
 if t=='case':
  body=paras(txt)
  for i in items:
   body+='<article class="case"><h4>'+esc(i['label'])+'</h4>'+paras(i.get('facts',i.get('text','')))
   if i.get('analysis'):body+='<details><summary>Análise</summary>'+paras(i['analysis'])+'</details>'
   body+='</article>'
  return '<div class="case-file"><h3>'+esc(title)+'</h3>'+body+'</div>'
 if t in ['sequence','questions']:
  items=[dict(i,label=re.sub(r'^\d+[. ]*','',i['label']).strip()) for i in items]
  return '<div class="questions"><h3>'+esc(title)+'</h3>'+paras(txt)+'<ol>'+''.join('<li>'+((('<strong>'+esc(i['label'])+'</strong> · ') if t=='sequence' and i['label'] else ''))+esc(i['text'])+'</li>' for i in items)+'</ol></div>'
 raise ValueError(t)
def diagram():
 s=(ROOT/'assets/unit08/diagram.html').read_text()
 tabs=re.search(r'<div class="tab-strip".*?</div>',s,re.S).group()
 tabs=tabs.replace('Um terceiro impede','Tentativa').replace('A decide parar','Desistência').replace('A impede o resultado','Arrependimento eficaz')
 drawing=s[s.index('<div class="drawing-paper"'):s.index('<div class="decision-note"')]
 finding=re.search(r'<aside class="finding coral".*?</aside>',s,re.S).group()
 return '<div class="diagram-block full-width"><p class="diagram-intro">Compare três hipóteses de homicídio doloso em que B sobrevive. O fato que muda é a causa da não consumação.</p>'+tabs+drawing+finding+'</div>'
def build():
 data=json.loads(DATA.read_text());sects=data['sections']
 nav=''.join('<li><a href="#'+esc(s['id'])+'"><span>'+f'{n:02}'+'</span>'+esc(s['title'])+'</a></li>' for n,s in enumerate(sects,1))
 content=''
 for n,s in enumerate(sects,1):
  content+='<section class="chapter" id="'+esc(s['id'])+'"><header class="chapter-head"><div class="chapter-n" aria-hidden="true">'+f'{n:02}'+'</div><div><h2>'+esc(s['title'])+'</h2><p class="chapter-intro">'+esc(s['intro'])+'</p></div></header><div class="chapter-body">'
  if s['id']=='s4':content+=diagram()
  content+=''.join(render_block(b) for b in s['blocks'])
  content+='<p class="original-link" lang="en">Source sections: '+esc(', '.join(re.match(r'\d+',x).group() for x in s['source_sections']))+' · <a href="unidade-08-original.html">Original complete reading</a></p></div></section>'
 css=ROOT/'assets/unit08/lesson.css';js=ROOT/'assets/unit08/lesson.js'
 asset=lambda p:'../../'+str(p.relative_to(ROOT))+'?v='+hashlib.sha256(p.read_bytes()).hexdigest()[:12]
 page='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tentativa e desistência · Teoria do Delito</title><link rel="stylesheet" href="%s"></head><body><a class="skip" href="#lesson">Pular para a leitura</a><nav class="page-nav"><a href="index.html">← Teoria do Delito</a><a href="unidade-08-original.html">Original complete reading ↗</a></nav><main class="lesson" id="lesson"><header class="lesson-header"><div class="running"><span>UNIDADE 08 · DIREITO PENAL</span><span>ARTS. 14–17 / CÓDIGO PENAL</span></div><h1>Tentativa e <em>desistência.</em></h1><p class="standfirst">Iter criminis, crime impossível, interrupção da execução e impedimento do resultado.</p><span class="unit-stamp" aria-hidden="true">08</span></header><nav class="index" aria-label="Conteúdo da unidade"><h2>NESTA UNIDADE</h2><ol>%s</ol></nav>%s<details class="editorial" lang="en"><summary>Sources and editorial changes</summary><p>This lesson reorganizes all fourteen sections of the selected unit-08 study guide. Repeated explanations are consolidated; the complete original reading remains available. Source-section references accompany each section. The visual cases are conditional study examples, not an automatic legal classifier.</p><p>The underlying guide is an AI-assisted synthesis, not a verified transcript of classroom teaching. The Brazilian Penal Code remains the legal reference; Roxin is comparative doctrine. See the <a href="../../experiments/unit08-research.md">design research record</a>, <a href="editorial.html">course editorial record</a> and <a href="https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm">official Penal Code</a>.</p></details><nav class="lesson-footer" aria-label="Navegação entre unidades"><a href="unidade-07.html">← Nexo causal e imputação objetiva</a><a href="unidade-09.html">Antijuridicidade →</a></nav></main><script src="%s" defer></script></body></html>'''%(asset(css),nav,content,asset(js))
 OUT.write_text(page)
 provenance_path=ROOT/'courses/teoria-do-delito/provenance.json'
 provenance=json.loads(provenance_path.read_text())
 publication=provenance.setdefault('editorial',{}).setdefault('unit08_publication',{})
 publication.update({'editorial_data':'../../tools/editorial/unit08.json','editorial_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'renderer':'../../tools/build_unit08.py','renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'authored_html_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source_sections':14,'authored_sections':len(sects)})
 provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'sections':len(sects),'output':str(OUT),'editorial_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest()}))
if __name__=='__main__':build()
