import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {JSDOM} from 'jsdom';
function demo(mobile=false){
 const dom=new JSDOM(readFileSync('docs/index.html','utf8'),{url:'https://example.test/',runScripts:'outside-only'});
 const queries=new Map();dom.window.matchMedia=q=>{
  if(!queries.has(q))queries.set(q,{matches:/(900|1150)px/.test(q)&&mobile,listeners:[],addEventListener(_,fn){this.listeners.push(fn);}});
  return queries.get(q);
 };
 dom.changeMedia=(query,matches)=>{const media=dom.window.matchMedia(query);media.matches=matches;media.listeners.forEach(fn=>fn({matches}));};
 dom.window.HTMLElement.prototype.scrollIntoView=function(){};
 const style=dom.window.document.createElement('style');style.textContent=readFileSync('docs/styles.css','utf8')+'\n'+readFileSync('docs/window.css','utf8');dom.window.document.head.append(style);
 dom.window.eval(readFileSync('docs/site.js','utf8'));
 dom.window.eval(readFileSync('docs/window.js','utf8'));
 return dom;
}
test('conversation navigation, meanings and focus filters preserve the reply',()=>{
 const dom=demo(),d=dom.window.document;
 const link=d.querySelector('[data-chat="backup"]');link.click();
 assert(d.querySelector('#backup').classList.contains('active'));
 d.querySelector('[data-focus="problem"]').click();
 assert(d.querySelector('#backup [data-kind="answer"]').classList.contains('dim'));
 assert(!d.querySelector('#backup [data-kind="problem"]').classList.contains('dim'));
 const bug=[...d.querySelectorAll('#backup .mk')].find(b=>b.textContent==='🐞');bug.focus();bug.click();
 assert.equal(d.querySelector('#mk-name').textContent,'Actual bug');
 assert(!d.querySelector('#app').classList.contains('pane-open'));
 d.querySelector('.marker-popover button').click();assert.equal(d.activeElement,bug);
 dom.window.close();
});
test('mobile pane isolates background and Escape restores the opener',()=>{
 const dom=demo(true),d=dom.window.document;
 const a=d.querySelector('[data-pane="colours"]');a.focus();a.click();
 assert.equal(d.querySelector('#thread').inert,true);
 d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape'}));
 assert.equal(d.querySelector('#thread').inert,false);assert.equal(d.activeElement,a);
 dom.window.close();
});
test('switching a viewed document requires confirmation; reopening it keeps edits',()=>{
 const dom=demo(),d=dom.window.document;
 const a=d.querySelector('a[data-file]');a.click();
 const frame=d.querySelector('#frame'),src=frame.getAttribute('src');
 dom.window.confirm=()=>{throw Error('Same document must not prompt');};a.click();assert.equal(frame.getAttribute('src'),src);
 dom.window.confirm=()=>false;
 d.querySelector('.ctx[data-file]').click();assert.equal(frame.getAttribute('src'),src);
 dom.window.close();
});
test('the demo preserves the approved marker vocabulary and efficient section placement',()=>{
 const dom=demo(),d=dom.window.document;
 const expected=['🧪','🛠️','⮑','✅','❌','👀','🐌','🐞','ⓘ','🫵','🤨','⚠️','❓','💡','⚖️','⛔','🧠','➕➕','🖥️','👉'];
 assert.deepEqual(new Set([...d.querySelectorAll('.conversation .mk')].map(x=>x.textContent)),new Set(expected));
 for(const b of d.querySelectorAll('.conversation .mk')){
   if(b.textContent!=='👉')assert.equal(b.parentElement.firstElementChild,b,'Marker precedes the section text');
   assert(!b.closest('blockquote'),'The answer marker must be outside the question quote');
   if(b.parentElement.classList.contains('sec'))assert(b.parentElement.children.length>2,'A single statement keeps its marker inline');
 }
 for(const p of d.querySelectorAll('[data-kind="answer"]')){
   assert(p.previousElementSibling.matches('blockquote.quote'));
   assert.equal(p.tagName,'P','The opening answer stays beside the return arrow');
   assert(p.textContent.replace('⮑','').trim(),'The arrow must have an opening answer');
 }
 dom.window.close();
});
test('skill names remain magenta serif with a separate working HTML link',()=>{
 const dom=demo(),d=dom.window.document;
 for(const name of d.querySelectorAll('.conversation .skill')){
   const style=dom.window.getComputedStyle(name);assert.equal(style.color,'var(--magenta)');assert.equal(dom.window.getComputedStyle(d.documentElement).getPropertyValue('--magenta'),'#ff00ff');assert.match(style.fontFamily,/Georgia/);
   const link=name.nextElementSibling;assert.equal(link.textContent,'↗');assert.equal(link.tagName,'A');assert.match(link.getAttribute('href'),/^\.\/skill\.html\?v=/);
   assert(readFileSync('docs/skill.html','utf8').includes('Response Preferences'));
 }
 const colours={red:'#ef4444',green:'#22c55e',orange:'#fb923c',cyan:'#67e8f9'};
 // JSDOM exposes CSS variables rather than resolving them into RGB. Verify both layers.
 for(const [name,colour] of Object.entries(colours)){
   assert.equal(dom.window.getComputedStyle(d.querySelector('.c-'+name)).color,'var(--'+name+')');
   assert.equal(dom.window.getComputedStyle(d.documentElement).getPropertyValue('--'+name),colour);
 }
 dom.window.close();
});

test('working markers use text size while final markers stay enlarged',()=>{
 const dom=demo(),d=dom.window.document,style=el=>dom.window.getComputedStyle(el);
 const working=[...d.querySelectorAll('.msg.assistant:not(.final) .mk')];
 assert(working.some(el=>el.textContent==='🧠'),'Show the small skill announcement too');
 for(const marker of working){assert.equal(style(marker).fontSize,style(marker.parentElement).fontSize);assert.equal(style(marker).verticalAlign,'baseline');}
 for(const marker of d.querySelectorAll('.msg.assistant.final .mk'))assert.equal(style(marker).fontSize,'32px');
 assert(d.querySelector('#format').textContent.includes('Working messages use small markers'));
 dom.window.close();
});

test('scanning cues preserve qualifications, colours, quotations and real links',()=>{
 const dom=demo(),d=dom.window.document;
 assert.equal(d.querySelectorAll('.quote u,.user u,code u,a u,u a,u code').length,0);
 for(const colour of ['c-cyan','c-green','c-orange','c-red'])assert(d.querySelector('.conversation .'+colour+' u'),'Each colour also demonstrates scanning cues');
 const cues=[...d.querySelectorAll('.conversation .assistant u')].map(x=>x.textContent);
 for(const clue of ['packed but not uploaded','no off-site copy from tonight','after restarting the app','cannot guarantee that a model always follows them'])assert(cues.includes(clue),'Retain decisive qualification: '+clue);
 for(const p of d.querySelectorAll('.conversation .assistant p')){
  if(p.closest('blockquote')||p.matches('.topic-reminder')||p.textContent==='Added beyond your request')continue;
  assert(p.querySelector('u'),'Assistant prose has scanning cues: '+p.textContent);
 }
 const u=d.querySelector('.conversation .assistant u');
 assert.equal(dom.window.getComputedStyle(u).textDecorationLine,'underline');
 assert.equal(u.closest('a'),null,'Underlines do not invent links');
 dom.window.close();
});

test('full annotation context keeps a separate short question before the answer',()=>{
 const dom=demo(),d=dom.window.document;
 const full=d.querySelector('.annotation-context');
 assert(full.textContent.includes('Earlier response:'));
 assert(full.textContent.includes('Your annotation:'));
 const reminder=full.nextElementSibling;
 assert(reminder.matches('blockquote.quote'));
 assert.equal(reminder.querySelector('a').getAttribute('href'),'#format-u3');
 assert(reminder.nextElementSibling.matches('p[data-kind="answer"]'));
 dom.window.close();
});

test('automated results stay uncoloured and manual success uses the computer marker',()=>{
 const dom=demo(),d=dom.window.document;
 const answer=d.querySelector('#export .final p[data-kind="answer"]');
 assert.equal(answer.firstElementChild.textContent,'⮑');
 assert(answer.querySelector('.c-cyan u').textContent.includes('export keeps every final frame'));
 assert(!answer.querySelector('.c-green'));
 assert(!answer.querySelector('.c-cyan').textContent.includes('restart'));
 const automated=d.querySelector('#export p[data-kind="test"]');
 assert(!automated.querySelector('.c-green'));
 const manual=d.querySelector('.manual-check');
 assert.equal(manual.querySelector('.mk').textContent,'🖥️');
 assert(manual.querySelector('.c-green').textContent.includes('manual playback check'));
 manual.querySelector('.mk').click();assert.equal(d.querySelector('#mk-name').textContent,'Computer Use');
 dom.window.close();
});

test('only final example replies have attention fingers',()=>{
 const dom=demo();
 for(const msg of dom.window.document.querySelectorAll('.msg.assistant')){
  assert.equal([...msg.querySelectorAll('.mk')].some(m=>['👉','🫵'].includes(m.textContent)),msg.classList.contains('final'));
 }
 dom.window.close();
});

test('window search, menu dismissal and agent handoff preserve local content',async()=>{
 const dom=demo(),d=dom.window.document;
 d.querySelector('.search-examples').click();
 const input=d.querySelector('#example-search');input.value='backup';input.dispatchEvent(new dom.window.Event('input'));
 assert.equal(d.querySelectorAll('.search-results button').length,1);
 d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape'}));
 assert.equal(d.querySelector('.window-popover'),null);assert.equal(d.activeElement,d.querySelector('.search-examples'));
 let copied;Object.defineProperty(dom.window.navigator,'clipboard',{value:{writeText:async text=>{copied=text;}}});
 const count=d.querySelectorAll('.conversation .msg').length;const draft=d.querySelector('#demo-draft');draft.value='Can I change the cyan?';d.querySelector('.demo-composer').dispatchEvent(new dom.window.Event('submit',{cancelable:true}));await new Promise(resolve=>setTimeout(resolve,0));
 assert(copied.includes('https://github.com/EthanSK/response-preferences'));assert(copied.endsWith('My question: Can I change the cyan?'));
 assert.equal(draft.value,'Can I change the cyan?');assert.equal(d.querySelectorAll('.conversation .msg').length,count);
 assert.match(d.querySelector('#local-status').textContent,/Paste into your agent task/);dom.window.close();
});

test('traffic lights preserve the page, restore focus and expand reversibly',()=>{
 const dom=demo(),d=dom.window.document,app=d.querySelector('#app');
 assert.equal(d.querySelector('.workspace-pill'),null);assert.equal(d.querySelectorAll('.traffic').length,3);
 d.querySelector('#demo-draft').value='Keep my question';
 for(const name of ['close-window','minimise-window']){
  const control=d.querySelector('.'+name);control.click();assert.equal(app.hidden,true);
  assert.equal(dom.window.getComputedStyle(app).display,'none');
  assert.equal(d.querySelector('.restore-preview').hidden,false);
  d.querySelector('.restore-preview button').click();assert.equal(app.hidden,false);
  assert.equal(d.activeElement,control);assert.equal(d.querySelector('#demo-draft').value,'Keep my question');
 }
 const expand=d.querySelector('.expand-window');expand.click();assert(d.body.classList.contains('demo-expanded'));assert.equal(expand.getAttribute('aria-pressed'),'true');
 expand.click();assert(!d.body.classList.contains('demo-expanded'));dom.window.close();
});

test('installation controls copy their exact visible instructions and preserve failure recovery',async()=>{
 const dom=demo(),d=dom.window.document;let copied;
 Object.defineProperty(dom.window.navigator,'clipboard',{value:{writeText:async text=>{copied=text;}}});
 for(const control of d.querySelectorAll('[data-copy-source]')){
  control.click();await Promise.resolve();
  assert.equal(copied,d.getElementById(control.dataset.copySource).textContent);
 }
 assert.equal(d.querySelector('#setup-prompt').textContent.trim(),readFileSync('docs/install-prompt.txt','utf8').trim());
 const style=dom.window.getComputedStyle(d.querySelector('#setup .primary-action'));
 assert.equal(style.color,'rgb(25, 25, 25)');assert.equal(style.backgroundColor,'rgb(229, 229, 231)');
 assert(d.querySelector('#setup-prompt').textContent.includes('preserve any local changes'));
 assert(d.querySelector('#setup-prompt').textContent.includes('Ask me before installing any future skill updates'));
 dom.window.navigator.clipboard.writeText=async()=>{throw Error('Clipboard denied');};
 const control=d.querySelector('[data-copy-source="setup-prompt"]');control.click();await new Promise(resolve=>setTimeout(resolve,0));
 assert.match(control.parentElement.querySelector('.copy-feedback').textContent,/Select the text/);
 assert.equal(dom.window.getSelection().toString(),d.querySelector('#setup-prompt').textContent);dom.window.close();
});

test('compact layouts dismiss the details card on resize and after choosing a destination',()=>{
 const dom=demo(),d=dom.window.document,card=d.querySelector('.details-card');assert.equal(card.hidden,false);
 dom.changeMedia('(max-width: 1150px)',true);assert.equal(card.hidden,true);assert(!d.querySelector('#app').classList.contains('details-open'));
 d.querySelector('.toggle-details').click();assert.equal(card.hidden,false);card.querySelector('a').click();assert.equal(card.hidden,true);dom.window.close();
});

test('the welcome route leads through all six conversations and returns from install details',()=>{
 const dom=demo(),d=dom.window.document;assert.equal(d.querySelector('.conversation.active').id,'welcome');
 assert.equal(d.querySelectorAll('.chat-list [data-chat]').length,6);
 for(const link of d.querySelectorAll('.chat-list [data-chat]'))assert(d.getElementById(link.dataset.chat));
 d.querySelector('[data-pane="install"]').click();assert(d.querySelector('#app').classList.contains('pane-open'));
 d.querySelector('[data-chat="setup"]').click();assert.equal(d.querySelector('.conversation.active').id,'setup');assert(!d.querySelector('#app').classList.contains('pane-open'));
 assert.equal(d.querySelectorAll('.glossary .mk').length,20);assert.match(d.querySelector('#markers-h').textContent,/Twenty/);dom.window.close();
});
test('mobile sidebar and editor isolate the background and restore it',async()=>{
 const dom=demo(true),d=dom.window.document;
 d.querySelector('.header-sidebar').click();await Promise.resolve();assert.equal(d.querySelector('#thread').inert,true);
 d.querySelector('.collapse-side').click();await Promise.resolve();assert.equal(d.querySelector('#thread').inert,false);
 d.querySelector('[data-pane="editor"]').click();await Promise.resolve();assert.equal(d.querySelector('#thread').inert,true);assert.equal(d.querySelector('#sidebar').inert,true);
 d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape'}));await Promise.resolve();assert.equal(d.querySelector('#thread').inert,false);dom.window.close();
});

test('every assistant example closes with a distinct topic reminder after its content',()=>{
 const dom=demo(),d=dom.window.document;
 for(const msg of d.querySelectorAll('.msg.assistant')){
  const reminders=msg.querySelectorAll('.topic-reminder');assert.equal(reminders.length,1);
  const reminder=reminders[0];assert.equal(msg.lastElementChild,reminder);
  assert.match(reminder.textContent,/^About: .+/);
  assert.equal(reminder.querySelectorAll('u,a,.mk').length,0);
  assert.equal(dom.window.getComputedStyle(reminder).color,'var(--topic)');
 }
 assert.equal(d.querySelectorAll('.user .topic-reminder,.quote .topic-reminder').length,0);
 assert.equal(dom.window.getComputedStyle(d.documentElement).getPropertyValue('--topic'),'#b8a4d9');
 assert(d.querySelector('#backup .final .topic-reminder').textContent.includes('release decision'));
 dom.window.close();
});

test('the first home reply previews the range and its marker controls open real explanations',()=>{
 const dom=demo(),d=dom.window.document,home=d.querySelector('#welcome'),first=home.querySelector('.final');
 for(const c of ['c-green','c-cyan','c-orange','c-red'])assert(first.querySelector('.'+c+' u'));
 assert.equal(first.querySelectorAll('.welcome-marker-range .mk').length,20);
 assert(home.querySelector('.assistant:not(.final) .skill'));
 assert(first.querySelector('.sec > .mk'));assert(first.querySelector('table'));
 assert(first.querySelector('a[data-file][href^="./viewer.html"]'));
 assert(first.querySelector('a[data-file][href^="./message.html"]'));
 assert(first.querySelector('a[href="#format-u3"]'));assert(first.querySelector('.notification-example'));
 const failure=[...first.querySelectorAll('.welcome-marker-range .mk')].find(x=>x.textContent==='❌');failure.click();
 assert.equal(d.querySelector('#mk-name').textContent,'Failure');assert(!d.querySelector('#app').classList.contains('pane-open'));assert.equal(d.querySelector('.marker-popover').getAttribute('aria-label'),'Failure');
 dom.window.close();
});

test('marker popovers toggle, dismiss with Escape and preserve the open document pane',()=>{
 const dom=demo(),d=dom.window.document,button=d.querySelector('.welcome-colours .mk');
 const classes=d.querySelector('#app').className;button.click();assert.equal(d.querySelector('#app').className,classes);assert(d.querySelector('.marker-popover'));
 button.click();assert(!d.querySelector('.marker-popover'));
 button.click();d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));assert(!d.querySelector('.marker-popover'));assert.equal(d.activeElement,button);
 d.querySelector('[data-pane="editor"]').click();button.click();d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));assert(d.querySelector('#app').classList.contains('pane-open'));
 button.click();dom.window.dispatchEvent(new dom.window.Event('resize'));assert(d.querySelector('.marker-popover'));
 d.body.dispatchEvent(new dom.window.Event('pointerdown',{bubbles:true}));assert(!d.querySelector('.marker-popover'));
 assert(!d.querySelector('#side-nav').textContent.includes('Full skill text'));
 dom.window.close();
});


test('planning and brainstorming share a working marker, explanation and filter',()=>{
 const dom=demo(),d=dom.window.document,example=d.querySelector('#welcome .planning-example');
 example.querySelector('.mk').click();
 assert.equal(d.querySelector('#mk-name').textContent,'Planning and brainstorming');
 assert.match(d.querySelector('.marker-popover').textContent,/Planned or proposed work/);
 d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
 d.querySelector('[data-focus="plan"]').click();
 assert(!example.classList.contains('dim'));
 assert(d.querySelector('#welcome [data-kind="success"]').classList.contains('dim'));
 assert(d.querySelector('#format .sec[data-kind="plan"] .mk'));
 dom.window.close();
});


test('test information uses the test marker without implying success or hiding limits',()=>{
 const dom=demo(),d=dom.window.document,example=d.querySelector('#welcome .testing-example');
 assert.match(example.textContent,/not covered/);
 assert(!example.querySelector('[class^="c-"]'));
 example.querySelector('.mk').click();
 assert.equal(d.querySelector('#mk-name').textContent,'Tests');
 assert.match(d.querySelector('.marker-popover').textContent,/coverage, progress and results/);
 d.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
 d.querySelector('[data-focus="test"]').click();
 assert(!example.classList.contains('dim'));
 assert(d.querySelector('#welcome [data-kind="info"]').classList.contains('dim'));
 assert.equal(d.querySelector('#export .assistant:not(.final) [data-kind="test"] .mk').textContent,'🧪');
 assert.equal(d.querySelector('#export .final [data-kind="test"] .mk').textContent,'🧪');
 assert.equal(d.querySelector('#backup [data-kind="problem"]:has(code) .mk').textContent,'🐞');
 dom.window.close();
});
