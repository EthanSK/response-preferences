import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {JSDOM} from 'jsdom';
function demo(mobile=false){
 const dom=new JSDOM(readFileSync('docs/index.html','utf8'),{url:'https://example.test/',runScripts:'outside-only'});
 dom.window.matchMedia=q=>({matches:q.includes('900px')&&mobile,addEventListener(){}});
 dom.window.HTMLElement.prototype.scrollIntoView=function(){};
 const style=dom.window.document.createElement('style');style.textContent=readFileSync('docs/styles.css','utf8');dom.window.document.head.append(style);
 dom.window.eval(readFileSync('docs/site.js','utf8'));
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
 d.querySelector('#pane-close').click();assert.equal(d.activeElement,bug);
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
 const expected=['⮑','✅','❌','👀','🐌','🐞','ⓘ','🫵','🤨','⚠️','❓','💡','⚖️','⛔','🎯','➕➕'];
 assert.deepEqual(new Set([...d.querySelectorAll('.conversation .mk')].map(x=>x.textContent)),new Set(expected));
 for(const b of d.querySelectorAll('.conversation .mk')){
   assert.equal(b.parentElement.firstElementChild,b,'Marker precedes the section text');
   assert(!b.closest('blockquote'),'The answer marker must be outside the question quote');
   if(b.parentElement.classList.contains('sec'))assert(b.parentElement.children.length>2,'A single statement keeps its marker inline');
 }
 for(const p of d.querySelectorAll('[data-kind="answer"]'))assert(p.previousElementSibling.matches('blockquote.quote'));
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
