import {basicSetup} from 'codemirror';
import {EditorState, StateField, StateEffect, Compartment} from '@codemirror/state';
import {EditorView, Decoration, keymap} from '@codemirror/view';
import {indentWithTab} from '@codemirror/commands';
import {openSearchPanel} from '@codemirror/search';
import {HighlightStyle, syntaxHighlighting, StreamLanguage} from '@codemirror/language';
import {tags} from '@lezer/highlight';
import {markdown} from '@codemirror/lang-markdown';
import {javascript} from '@codemirror/lang-javascript';
import {python} from '@codemirror/lang-python';
import {json} from '@codemirror/lang-json';
import {html} from '@codemirror/lang-html';
import {css} from '@codemirror/lang-css';
import {sql} from '@codemirror/lang-sql';
import {yaml} from '@codemirror/legacy-modes/mode/yaml';
import {shell} from '@codemirror/legacy-modes/mode/shell';
import {rust} from '@codemirror/legacy-modes/mode/rust';
import {go} from '@codemirror/legacy-modes/mode/go';
import {renderMarkdown, selectPassage} from './markdown.js';
import {decodeText, writeIfUnchanged} from './files.js';

const $ = id => document.getElementById(id);
const data = JSON.parse($('document-data').textContent);
const language = new Compartment();
const targetEffect = StateEffect.define();
const selectedLine = StateField.define({
  create: () => Decoration.none,
  update(value, transaction) {
    value = value.map(transaction.changes);
    for (const effect of transaction.effects) if (effect.is(targetEffect)) value = Decoration.set([Decoration.line({class: 'cm-target-line'}).range(effect.value)]);
    return value;
  },
  provide: field => EditorView.decorations.from(field)
});
const colours = HighlightStyle.define([
  {tag: tags.keyword, color: '#b18cdb'}, {tag: [tags.string, tags.attributeValue], color: '#589d76'},
  {tag: [tags.number, tags.bool, tags.null], color: '#bd854d'}, {tag: tags.comment, color: '#8a90a3', fontStyle: 'italic'},
  {tag: [tags.function(tags.variableName), tags.typeName], color: '#6c9cd5'},
  {tag: tags.heading, color: '#ae88d4', fontWeight: 'bold'}, {tag: tags.link, color: '#719fd1'},
  {tag: tags.strong, fontWeight: 'bold'}, {tag: tags.emphasis, fontStyle: 'italic'}
]);
function modeFor(name) {
  const ext = name.split('.').pop().toLowerCase();
  const modes = {md: () => markdown(), markdown: () => markdown(), js: () => javascript(), mjs: () => javascript(), cjs: () => javascript(), jsx: () => javascript({jsx:true}), ts: () => javascript({typescript:true}), tsx: () => javascript({typescript:true,jsx:true}), py: python, json, html, htm:html, css, sql, yaml: () => StreamLanguage.define(yaml), yml: () => StreamLanguage.define(yaml), sh: () => StreamLanguage.define(shell), zsh: () => StreamLanguage.define(shell), bash: () => StreamLanguage.define(shell), rs: () => StreamLanguage.define(rust), go: () => StreamLanguage.define(go)};
  return modes[ext]?.() || [];
}
let name = data.name || 'document.md', baseline = data.source, rawBaseline = data.source, fileHandle = null, busy = false;
let images = data.images || {}, links = data.links || {}, currentMode = /\.(md|markdown)$/i.test(name) ? 'preview' : 'edit';
let targetLine = Number(data.line) || 1, renderTimer, sourceEol = data.source.includes('\r\n') ? '\r\n' : '\n', sourceBom = data.source.startsWith('\ufeff');
const normalise = text => text.replace(/^\ufeff/, '').replace(/\r\n?/g, '\n');
baseline = normalise(baseline);
function say(message) {$('status').textContent = message;}
function isDirty() {return editor.state.doc.toString() !== baseline;}
function updateDirty() {
  const dirty = isDirty(); $('dirty').textContent = dirty ? 'Unsaved changes' : fileHandle ? 'File opened' : 'Snapshot';
  $('dirty').classList.toggle('unsaved', dirty); $('save').disabled = !fileHandle || busy || !dirty;
}
const editor = new EditorView({parent:$('editor'), state:EditorState.create({doc:baseline, extensions:[
  basicSetup, keymap.of([indentWithTab, {key:'Mod-s', run:() => {fileHandle ? saveFile() : downloadFile(); return true;}}]),
  language.of(modeFor(name)), syntaxHighlighting(colours), selectedLine,
  EditorView.contentAttributes.of({'aria-label':'Document source'}),
  EditorView.updateListener.of(update => {if (update.docChanged) {updateDirty();clearTimeout(renderTimer);renderTimer=setTimeout(render,180);}})
]})});
function render() {
  if (/\.(md|markdown)$/i.test(name)) $('preview').innerHTML = renderMarkdown(editor.state.doc.toString(), {images,links});
  else {const pre=document.createElement('pre');pre.textContent=editor.state.doc.toString();$('preview').replaceChildren(pre);}
  $('line').max=editor.state.doc.lines;
}
function jump(value, fromHash = false) {
  const line=Number(value), total=editor.state.doc.lines;
  if (!Number.isInteger(line) || line<1 || line>total) {say(`Enter a line from 1 to ${total}.`);return;}
  targetLine=line;$('line').value=line;
  if(!fromHash) {try {history.replaceState(null,'','#L'+line);} catch { /* file viewers can disable history */ }}
  const pos=editor.state.doc.line(line).from;
  editor.dispatch({effects:[targetEffect.of(pos),EditorView.scrollIntoView(pos,{y:'center'})],selection:{anchor:pos}});
  $('preview').querySelectorAll('.selected').forEach(el=>el.classList.remove('selected','pulse'));
  const passage=selectPassage($('preview'),line);
  if(passage) {passage.classList.add('selected');void passage.offsetWidth;passage.classList.add('pulse');if(currentMode!=='edit') requestAnimationFrame(()=>passage.scrollIntoView({block:'center',behavior:'instant'}));}
  say(`Line ${line}${passage && currentMode!=='edit' ? ` · passage spans lines ${passage.dataset.start}–${passage.dataset.end}` : ''}`);
}
function setMode(mode) {
  currentMode=mode;$('workspace').dataset.mode=mode;
  document.querySelectorAll('[data-mode]').forEach(el=>{if(el.tagName==='BUTTON')el.setAttribute('aria-pressed',String(el.dataset.mode===mode));});
  render();requestAnimationFrame(()=>{editor.requestMeasure();jump(Math.min(targetLine,editor.state.doc.lines),true);});
}
function confirmDiscard() {return !isDirty() || confirm('You have unsaved changes that opening another file will discard.');}
async function loadFile(file, handle=null) {
  if(file.size>5*1024*1024) throw Error('This file is larger than 5 MB. Open a smaller text file.');
  const text=decodeText(await file.arrayBuffer());
  name=file.name;rawBaseline=text;baseline=normalise(text);sourceEol=text.includes('\r\n')?'\r\n':'\n';sourceBom=text.startsWith('\ufeff');
  fileHandle=handle;images={};links={};
  editor.setState(EditorState.create({doc:baseline,extensions:[basicSetup,keymap.of([indentWithTab,{key:'Mod-s',run:()=>{fileHandle?saveFile():downloadFile();return true;}}]),language.of(modeFor(name)),syntaxHighlighting(colours),selectedLine,EditorView.contentAttributes.of({'aria-label':'Document source'}),EditorView.updateListener.of(update=>{if(update.docChanged){updateDirty();clearTimeout(renderTimer);renderTimer=setTimeout(render,180);}})]}));
  $('filename').textContent=name;$('file-note').textContent='Opened from disk · does not update automatically';
  $('snapshot-note').textContent=handle?'Save writes to the file you picked. Download copy creates a separate file.':'Download copy to keep your edits. The file you opened is unchanged.';
  targetLine=1;setMode(/\.(md|markdown)$/i.test(name)?'preview':'edit');updateDirty();
}
async function openFile() {
  if(busy || !confirmDiscard()) return;
  if(!window.showOpenFilePicker) {$('file-input').click();return;}
  try {const [handle]=await window.showOpenFilePicker({multiple:false});await loadFile(await handle.getFile(),handle);}
  catch(error) {if(error.name!=='AbortError') say('Could not open this file. '+error.message);}
}
function outputText() {return (sourceBom?'\ufeff':'') + editor.state.doc.toString().replace(/\n/g,sourceEol);}
async function saveFile() {
  if(!fileHandle || busy || !isDirty()) return;
  busy=true;updateDirty();say('Saving...');
  try {
    // Capture the revision being saved: edits made during the write stay marked unsaved.
    const savedRevision=editor.state.doc.toString(), savedText=outputText();
    await writeIfUnchanged(fileHandle,rawBaseline,savedText);
    rawBaseline=savedText;baseline=savedRevision;say('Saved');
  } catch(error) {say('Failed to save. '+error.message);}
  finally {busy=false;updateDirty();}
}
function downloadFile() {
  const url=URL.createObjectURL(new Blob([outputText()],{type:'text/plain;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
  say('Download started. The file you opened is unchanged.');
}
$('filename').textContent=name;$('file-note').textContent=data.generated?`Snapshot · ${data.generated}`:'Local document';
document.querySelectorAll('button[data-mode]').forEach(button=>button.onclick=()=>setMode(button.dataset.mode));
$('jump-form').onsubmit=event=>{event.preventDefault();jump($('line').value);};
$('search').onclick=()=>{if(currentMode==='preview')setMode('edit');openSearchPanel(editor);editor.focus();};
$('open').onclick=openFile;$('save').onclick=saveFile;$('download').onclick=downloadFile;
$('file-input').onchange=async()=>{const file=$('file-input').files[0];if(file)try{await loadFile(file);}catch(error){say('Could not open this file. '+error.message);}finally{$('file-input').value='';}};
$('theme').onclick=()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==='light'?'dark':'light';};
$('preview').onclick=event=>{const unavailable=event.target.closest('[data-unavailable]');if(unavailable){event.preventDefault();say('Open the linked file from disk. It is not included in this viewer.');}};
addEventListener('beforeunload',event=>{if(isDirty()){event.preventDefault();event.returnValue='';}});
addEventListener('hashchange',()=>{const match=location.hash.match(/^#L(\d+)$/);if(match)jump(+match[1],true);});
const hash=location.hash.match(/^#L(\d+)$/);if(hash)targetLine=+hash[1];
targetLine=Math.min(Math.max(targetLine,1),editor.state.doc.lines);render();setMode(currentMode);updateDirty();
