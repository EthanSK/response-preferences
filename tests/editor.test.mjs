import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {JSDOM,VirtualConsole} from 'jsdom';

function boot(document, setup = () => {}) {
  const template=fs.readFileSync(new URL('../assets/viewer.html',import.meta.url),'utf8');
  const page=template.replace('__DOCUMENT__',JSON.stringify(document));
  const errors=[];const virtualConsole=new VirtualConsole();virtualConsole.on('jsdomError',error=>errors.push(error.message));
  const dom=new JSDOM(page,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://example.invalid/viewer.html',virtualConsole,beforeParse(window){
    window.TextDecoder=TextDecoder;window.TextEncoder=TextEncoder;
    window.Range.prototype.getClientRects=()=>[];
    window.Range.prototype.getBoundingClientRect=()=>({top:0,left:0,right:0,bottom:0,width:0,height:0});
    window.HTMLElement.prototype.scrollIntoView=()=>{};
    window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});
    setup(window);
  }});
  return {dom,errors};
}

test('bundled editor boots, changes views, jumps to line and opens search without a browser',async()=>{
  const {dom,errors}=boot({name:'example.md',source:'# Heading\n\n- first\n- second\n',line:4,images:{},links:{}});
  try {
    await new Promise(resolve=>setTimeout(resolve,100));
    const d=dom.window.document;
    assert.deepEqual(errors,[]);
    assert.equal(d.querySelector('#filename').textContent,'example.md');
    assert.equal(d.querySelector('.selected').textContent.trim(),'second');
    assert.equal(d.querySelector('#save').disabled,true);
    d.querySelector('button[data-mode="edit"]').click();
    await new Promise(resolve=>setTimeout(resolve,30));
    assert.equal(d.querySelector('#workspace').dataset.mode,'edit');
    assert.ok(d.querySelector('.cm-editor .cm-content'));
    d.querySelector('#line').value='1';d.querySelector('#jump-form').dispatchEvent(new dom.window.Event('submit',{cancelable:true}));
    assert.equal(dom.window.location.hash,'#L1');
    d.querySelector('#search').click();assert.ok(d.querySelector('.cm-search'));
    assert.deepEqual(errors,[]);
  } finally {dom.window.close();}
});

test('opened-file editing saves the picked file, refuses external edits and preserves unsaved work',async()=>{
  let disk='# Original\n', writes=0, confirmations=0;
  const handle={
    async getFile(){const text=disk;return {name:'picked.md',size:text.length,arrayBuffer:async()=>new TextEncoder().encode(text).buffer};},
    async createWritable(){return {async write(text){disk=text;writes++;},async close(){},async abort(){}};}
  };
  const {dom,errors}=boot({name:'snapshot.md',source:'# Snapshot\n',line:1,images:{},links:{}},window=>{
    window.showOpenFilePicker=async()=>[handle];
    window.confirm=()=>{confirmations++;return false;};
  });
  const settle=()=>new Promise(resolve=>setTimeout(resolve,220));
  try{
    await settle();const d=dom.window.document;
    d.querySelector('#open').click();await settle();
    assert.equal(d.querySelector('#filename').textContent,'picked.md');
    assert.equal(d.querySelector('#dirty').textContent,'File opened');
    assert.equal(d.querySelector('#save').disabled,true);
    const replace=async(from,to)=>{
      d.querySelector('#search').click();
      for(const [name,value] of [['search',from],['replace',to]]){
        const input=d.querySelector(`.cm-search input[name="${name}"]`);input.value=value;
        input.dispatchEvent(new dom.window.Event('change',{bubbles:true}));
      }
      [...d.querySelectorAll('.cm-search button')].find(b=>b.textContent==='replace all').click();await settle();
    };
    await replace('Original','Saved');
    assert.equal(d.querySelector('#dirty').textContent,'Unsaved changes');
    assert.equal(d.querySelector('#save').disabled,false);
    d.querySelector('#save').click();await settle();
    assert.equal(disk,'# Saved\n');assert.equal(writes,1);
    assert.equal(d.querySelector('#dirty').textContent,'File opened');
    assert.equal(d.querySelector('#save').disabled,true);
    await replace('Saved','My draft');disk='# Changed somewhere else\n';
    d.querySelector('#save').click();await settle();
    assert.match(d.querySelector('#status').textContent,/Failed to save.*changed somewhere else/);
    assert.equal(writes,1);assert.equal(disk,'# Changed somewhere else\n');
    assert.equal(d.querySelector('#dirty').textContent,'Unsaved changes');
    d.querySelector('#open').click();await settle();
    assert.equal(confirmations,1);assert.match(d.querySelector('#preview').textContent,/My draft/);
    const leaving=new dom.window.Event('beforeunload',{cancelable:true});dom.window.dispatchEvent(leaving);
    assert.equal(leaving.defaultPrevented,true);assert.deepEqual(errors,[]);
  }finally{dom.window.close();}
});

test('compact chrome keeps accessible names, theme toggle, save state and status messages',async()=>{
  const {dom,errors}=boot({name:'notes.md',source:'# Title\n\nBody text.\n',line:3,images:{},links:{}});
  try {
    await new Promise(resolve=>setTimeout(resolve,100));
    const d=dom.window.document, root=d.documentElement;
    assert.deepEqual(errors,[]);
    // Icon-only actions keep their names; the save tooltip explains why it is disabled.
    for (const [id,name] of [['search','Search'],['open','Open file'],['save','Save'],['download','Download copy'],['theme','Switch colour theme']]) assert.equal(d.getElementById(id).getAttribute('aria-label'),name);
    assert.match(d.querySelector('#save').title,/Open a file/);
    assert.equal(d.querySelector('#filename').title,'notes.md');
    assert.equal(d.querySelector('#dirty').textContent,'Snapshot');
    assert.equal(d.querySelector('#preview').getAttribute('tabindex'),'0');
    // Theme starts from the (stubbed, dark) system preference and flips explicitly.
    assert.equal(root.dataset.theme,'dark');
    d.querySelector('#theme').click();assert.equal(root.dataset.theme,'light');
    d.querySelector('#theme').click();assert.equal(root.dataset.theme,'dark');
    // The initial line highlight is applied with its arrival animation and reported in the status bar.
    assert.ok(d.querySelector('#preview .selected.pulse'));
    assert.match(d.querySelector('#status').textContent,/^Line 3/);
    // Three lines plus the trailing newline give CodeMirror four lines; out-of-range jumps report that bound.
    d.querySelector('#line').value='99';d.querySelector('#jump-form').dispatchEvent(new dom.window.Event('submit',{cancelable:true}));
    assert.equal(d.querySelector('#status').textContent,'Enter a line from 1 to 4.');
    assert.deepEqual(errors,[]);
  } finally {dom.window.close();}
});
