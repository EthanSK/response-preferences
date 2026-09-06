(()=>{
'use strict';
const d=document;d.documentElement.classList.add('js');
const norm=s=>s.replace(/\uFE0F/g,'').trim();
const M={
'⮑':['Direct answer','A direct answer to your question. The arrow stays beside the opening answer, even when a table or list follows. The question sits in a quote above it; the answer makes sense without rereading it.'],
'🖥':['Computer Use','Manual browser/app interaction and tests, with explicit status wording. Green highlights confirmed manual success; failed or incomplete checks are not green. Automated tests and lint use ordinary text.'],
'✅':['Confirmed success','Only confirmed success or completion, never a general acknowledgement or a default prefix.'],
'❌':['Failure','An actual failure, including a check that itself could not run.'],
'👀':['Starting a check','Only when starting to look, check, inspect or review. A finished review reports its outcome with ✅, 🐞 or ❌ instead.'],
'🐌':['Work in progress','Work that is actively underway right now, including counts or percentages. Not for finished work, history, or things you still have to do.'],
'🐞':['Actual bug','An actual bug being reported. Not plans to look for bugs, test activity, or incomplete verification.'],
'ⓘ':['Information','Information, explanations and status summaries. A new ⓘ section starts when the purpose changes; a result section does not cover the explanation after it.'],
'👉':['Read this','The most useful takeaway to read, remember or continue from. Only the final reply uses an attention finger: normally one, with two only for distinct important items. Working updates have none.'],
'🫵':['Your action','An outstanding action or decision for you.'],
'🤨':['Unexpected','A weird or unexpected point.'],
'\u26A0':['Caution','A caution. Orange marks the phrase that matters; red is kept for critical must-read text.'],
'❓':['Missing information','Uncertainty, or information the assistant does not have.'],
'💡':['Recommendation','A recommendation, including minor non-bug improvements.'],
'\u2696':['Trade-offs','Trade-offs between options.'],
'⛔':['External blocker','A blocker outside the task that stops progress.'],
'🧠':['Skill use','A skill-use announcement: Skill use, the skill name in upright magenta serif, a brief reason, and a separate ↗ that opens the full skill. The response-preferences skill itself is applied silently unless you ask about it.'],
'➕➕':['Added beyond your request','Work added beyond what you asked for. Always the doubled marker, never a single ➕.']
};
const $=s=>d.querySelector(s),$$=s=>[...d.querySelectorAll(s)];
const app=$('#app'),side=$('#sidebar'),menu=$('#menu-toggle'),pane=$('#pane'),paneTitle=$('#pane-title'),chatTitle=$('#chat-title'),note=$('#focus-note'),frame=$('#frame'),frameCap=$('#frame-cap'),frameOpen=$('#frame-open');
const chats=$$('.conversation'),panels=$$('.panel'),reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
let kind='all', paneOpener=null; const mobile=matchMedia('(max-width: 900px)');
const applyFilter=()=>$$('[data-kind]').forEach(el=>el.classList.toggle('dim',kind!=='all'&&el.dataset.kind!==kind));
const closeMenu=()=>{side.classList.remove('open');menu.setAttribute('aria-expanded','false');};
function showChat(id){const c=chats.find(x=>x.id===id);if(!c)return false;chats.forEach(x=>x.classList.toggle('active',x===c));chatTitle.textContent=c.dataset.title;$$('[data-chat]').forEach(a=>a.setAttribute('aria-current',a.dataset.chat===id?'page':'false'));closeMenu();return true;}
function showPane(id,focus){if(!pane.contains(d.activeElement))paneOpener=d.activeElement;const p=panels.find(x=>x.id===id);if(!p)return false;panels.forEach(x=>x.classList.toggle('active',x===p));app.classList.add('pane-open');paneTitle.textContent=p.dataset.title;$$('[data-pane]').forEach(a=>a.setAttribute('aria-current',a.dataset.pane===id?'true':'false'));pane.scrollTop=0;if(mobile.matches){side.inert=true;$('#thread').inert=true;}if(focus){const h=p.querySelector('h2');if(h)h.focus({preventScroll:true});}return true;}
function closePane(){app.classList.remove('pane-open');side.inert=false;$('#thread').inert=false;if(paneOpener&&paneOpener.isConnected)paneOpener.focus({preventScroll:true});$$('[data-pane]').forEach(a=>a.setAttribute('aria-current','false'));if(panels.some(p=>'#'+p.id===location.hash))history.replaceState(null,'',location.pathname+location.search);}
function flash(t){t.scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'});if(!t.hasAttribute('tabindex'))t.setAttribute('tabindex','-1');t.focus({preventScroll:true});t.classList.add('flash');setTimeout(()=>t.classList.remove('flash'),1600);}
function showMarker(symbol){const m=M[norm(symbol)];if(!m)return;$('#mk-symbol').textContent=symbol;$('#mk-name').textContent=m[0];$('#mk-meaning').textContent=m[1];showPane('marker',true);}
function openFile(a){const src=a.getAttribute('href');if(frame.getAttribute('src')!==src){if(frame.dataset.opened&&!confirm('Opening another document replaces this pane. Download any edits first. Continue?'))return;frame.src=src;frame.dataset.opened='true';}frameOpen.href=src;frameCap.textContent=a.dataset.file;showPane('editor',true);}
function route(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}if(!id||showChat(id)||showPane(id,true))return;const t=d.getElementById(id),c=t&&t.closest('.conversation');if(!c)return;showChat(c.id);flash(t);}
$$('.mk').forEach(b=>{const symbol=b.textContent.trim(),m=M[norm(symbol)];if(!m)return;b.setAttribute('aria-label',m[0]+' marker '+symbol);b.title=m[0];b.addEventListener('click',()=>showMarker(symbol));});
$$('[data-chat]').forEach(a=>a.addEventListener('click',()=>showChat(a.dataset.chat)));
$$('[data-pane]').forEach(a=>a.addEventListener('click',()=>showPane(a.dataset.pane,true)));
$$('a[data-file]').forEach(a=>a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();openFile(a);}));
$$('a.ctx[href^="#"]').forEach(a=>a.addEventListener('click',e=>{const t=d.getElementById(a.hash.slice(1));if(!t)return;e.preventDefault();flash(t);}));
$$('[data-focus]').forEach(b=>b.addEventListener('click',()=>{kind=b.dataset.focus;$$('[data-focus]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));applyFilter();note.textContent=kind==='all'?'Showing whole replies. Click any marker to see its meaning.':'Emphasising '+b.textContent.trim()+'; other sections are dimmed.';}));
$('#pane-close').addEventListener('click',closePane);
menu.addEventListener('click',()=>{const open=side.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
d.addEventListener('keydown',e=>{if(e.key!=='Escape')return;if(app.classList.contains('pane-open'))closePane();closeMenu();});
$('#copy-install').addEventListener('click',async()=>{const s=$('#copy-status');try{await navigator.clipboard.writeText('git clone https://github.com/EthanSK/response-preferences.git ~/.codex/skills/response-preferences');s.textContent='Command copied.';}catch{s.textContent='Could not copy. Select the command above instead.';}});
mobile.addEventListener('change',()=>{const blocked=mobile.matches&&app.classList.contains('pane-open');side.inert=blocked;$('#thread').inert=blocked;});
addEventListener('hashchange',route);
showChat(chats[0].id);route();
})();
