import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {renderMarkdown,selectPassage} from '../src/markdown.js';

test('live resources require explicit registration and never enable arbitrary relative fetches',()=>{
  const capability='a'.repeat(43);
  const source='[Reference](notes.md)\n\n![Local](image.png)\n\n![Unregistered](other.png)';
  const options={live:true,links:{'notes.md':'/index.html?doc='+capability},images:{'image.png':'/api/resource?doc='+capability}};
  const doc=new JSDOM(renderMarkdown(source,options)).window.document;
  assert.equal(doc.querySelector('a').getAttribute('href'),options.links['notes.md']);
  assert.equal(doc.querySelectorAll('img').length,1);
  assert.equal(doc.querySelector('img').getAttribute('src'),options.images['image.png']);
  const snapshot=new JSDOM(renderMarkdown(source,{...options,live:false})).window.document;
  assert.equal(snapshot.querySelector('a').getAttribute('href'),'#');
  assert.equal(snapshot.querySelectorAll('img').length,0);
});

test('skill frontmatter stays compact without shifting document source lines',()=>{
  const doc=new JSDOM(renderMarkdown('---\nname: example\ndescription: A skill\n---\n\n# Example\n')).window.document;
  assert.equal(doc.querySelector('details summary').textContent,'Skill metadata');
  assert.equal(selectPassage(doc,3).dataset.start,'1');
  assert.equal(selectPassage(doc,6).textContent,'Example');
});

test('selects the correct repeated list entry and nested entry by parser source line',()=>{
  const source='# Heading\n\n- repeated\n- repeated\n  - child\n\nAfter.\n';
  const doc=new JSDOM(renderMarkdown(source)).window.document;
  assert.equal(selectPassage(doc,4).dataset.start,'4');
  assert.equal(selectPassage(doc,5).dataset.start,'5');
  assert.equal(selectPassage(doc,7).textContent,'After.');
});
test('raw HTML, event handlers, javascript links and remote image requests are inert',()=>{
  const source='<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n[bad](javascript:alert(1))\n\n![tracker](https://example.com/pixel)';
  const doc=new JSDOM(renderMarkdown(source)).window.document;
  assert.equal(doc.querySelector('script,img,[onerror]'),null);
  assert.equal(doc.querySelector('a[href^="javascript:"]'),null);
});
test('fenced code gets syntax tokens and source mapping; embedded images only use allowlisted data',()=>{
  const doc=new JSDOM(renderMarkdown('```js\nconst x = "hello";\n```\n\n![example](image.png)',{images:{'image.png':'data:image/png;base64,aGVsbG8='}})).window.document;
  assert.ok(doc.querySelector('.hljs-keyword'));
  assert.equal(selectPassage(doc,2).dataset.start,'1');
  assert.ok(doc.querySelector('img[src^="data:image/png"]'));
});
test('reference links, duplicate heading anchors, table and CRLF line mapping remain usable',()=>{
  const doc=new JSDOM(renderMarkdown('# Same\r\n\r\n# Same\r\n\r\n[Docs][ref]\r\n\r\n[ref]: https://example.com\r\n')).window.document;
  assert.ok(doc.querySelector('#same-1'));
  assert.equal(selectPassage(doc,5).dataset.start,'5');
  assert.equal(doc.querySelector('a').href,'https://example.com/');
});
