import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {JSDOM} from 'jsdom';
function demo(mobile=false){
 const dom=new JSDOM(readFileSync('docs/index.html','utf8'),{url:'https://example.test/',runScripts:'outside-only'});
 dom.window.matchMedia=q=>({matches:q.includes('900px')&&mobile,addEventListener(){}});
 dom.window.HTMLElement.prototype.scrollIntoView=function(){};
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
