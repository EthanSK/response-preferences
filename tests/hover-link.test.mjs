import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync,spawnSync} from 'node:child_process';
import MarkdownIt from 'markdown-it';
const parser=new MarkdownIt();
const helper=new URL('../scripts/hover-link.py',import.meta.url).pathname;
const link=text=>execFileSync('python3',[helper,'-'],{input:text,encoding:'utf8'}).trimEnd();
const links=source=>parser.parseInline(source,{})[0].children.filter(t=>t.type==='link_open');

test('a type expression breaks a raw angle destination but the helper preserves it as one link',()=>{
  const text="What is onlyIfTag: NonNullable<Result['Tag']>; for?";
  assert.equal(links(`[↗](</${text}>)`).length,0);
  const parsed=links(link(text));
  assert.equal(parsed.length,1);
  assert.equal(decodeURIComponent(parsed[0].attrGet('href')),'/'+text);
});

test('source punctuation, entities, literal URL escapes and Unicode survive parsing unchanged',()=>{
  for(const text of [
    'A < B > C, (nested (words)), [x], "quotes" and \'apostrophes\'',
    'C:\\Users\\folder; \\<escaped> and &copy; &amp; &#65;',
    'Keep 100% and literal %20, %2F, %3C; #fragment?x=y&z=1',
    '/leading/path and //not-a-server/path',
    'What’s café £5 — 日本語 🧪 for?',
    '  leading and trailing spaces  ',
  ]) {
    const parsed=links(link(text));
    assert.equal(parsed.length,1,text);
    const href=parsed[0].attrGet('href');
    assert.ok(href.startsWith('/')&&!href.startsWith('//'));
    assert.equal(decodeURIComponent(href),'/'+text);
  }
});

test('multiline and control-character input requests the real viewer instead of dropping words',()=>{
  for(const text of ['', 'one\ntwo', 'one\rtwo', 'one\ttwo', 'one\0two', 'one\u2028two']) {
    const result=spawnSync('python3',[helper,'-'],{input:text,encoding:'utf8'});
    assert.equal(result.status,2);
    assert.equal(result.stdout,'');
    assert.match(result.stderr,/real context viewer/);
  }
});
