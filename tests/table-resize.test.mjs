import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {renderMarkdown} from '../src/markdown.js';
import {resizeTables} from '../src/table-resize.js';

const source = '| Name | Details | State |\n| --- | --- | --- |\n| Alpha | Long text | Ready |\n';
function setup(widths = [120, 240, 120]) {
  const dom = new JSDOM('<article></article>', {pretendToBeVisual:true});
  const root = dom.window.document.querySelector('article'), saved = new Map();
  let cleanup;
  const render = () => {
    cleanup?.(); root.innerHTML = renderMarkdown(source); cleanup = resizeTables(root, saved);
    [...root.querySelectorAll('th')].forEach((cell, index) => {
      cell.getBoundingClientRect = () => ({width:parseFloat(root.querySelectorAll('col')[index].style.width) || widths[index]});
    });
    for (const handle of root.querySelectorAll('.column-resizer')) {
      handle.setPointerCapture = () => {}; handle.hasPointerCapture = () => false;
    }
  };
  const pointer = (type, x, extra = {}) => {
    const event = new dom.window.Event(type, {bubbles:true, cancelable:true});
    Object.assign(event, {button:0, isPrimary:true, pointerId:1, clientX:x, ...extra}); return event;
  };
  const values = () => [...root.querySelectorAll('col')].map(col => parseFloat(col.style.width));
  render();
  return {dom, root, saved, render, pointer, values, dispose:() => {cleanup(); dom.window.close();}};
}

test('drag resizes adjoining columns, bounds their minimum and preserves table text', () => {
  const s=setup(); try {
    const before=s.root.textContent, h=s.root.querySelector('.column-resizer');
    h.dispatchEvent(s.pointer('pointerdown',120)); h.dispatchEvent(s.pointer('pointermove',180));
    assert.deepEqual(s.values(),[180,180,120]);
    h.dispatchEvent(s.pointer('pointermove',900)); assert.deepEqual(s.values(),[312,48,120]);
    h.dispatchEvent(s.pointer('pointerup',900)); assert.equal(s.root.classList.contains('resizing-table'),false);
    assert.equal(s.root.textContent,before); assert.equal(s.root.querySelector('table').dataset.start,'1');
    h.dispatchEvent(s.pointer('pointermove',140)); assert.deepEqual(s.values(),[312,48,120]);
  } finally {s.dispose();}
});

test('keyboard widths survive rerender and double-click restores automatic layout', () => {
  const s=setup(); try {
    s.root.querySelector('.column-resizer').dispatchEvent(new s.dom.window.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true,cancelable:true}));
    assert.deepEqual(s.values(),[130,230,120]); s.render(); assert.deepEqual(s.values(),[130,230,120]);
    const h=s.root.querySelector('.column-resizer');
    h.dispatchEvent(new s.dom.window.KeyboardEvent('keydown',{key:'ArrowLeft',shiftKey:true,bubbles:true,cancelable:true}));
    assert.deepEqual(s.values(),[129,231,120]);
    h.dispatchEvent(new s.dom.window.MouseEvent('dblclick',{bubbles:true}));
    assert.equal(s.saved.size,0); assert.equal(s.root.querySelector('table').style.tableLayout,'');
  } finally {s.dispose();}
});

test('Escape restores the previous widths and a rerender releases active drag listeners', () => {
  const s=setup(); try {
    let h=s.root.querySelector('.column-resizer');
    h.dispatchEvent(s.pointer('pointerdown',120)); h.dispatchEvent(s.pointer('pointermove',180));
    s.dom.window.document.dispatchEvent(new s.dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));
    assert.deepEqual(s.values(),[120,240,120]); assert.equal(s.saved.size,0);
    h.dispatchEvent(s.pointer('pointerdown',120)); h.dispatchEvent(s.pointer('pointermove',160));
    s.render(); h.dispatchEvent(s.pointer('pointermove',190));
    assert.deepEqual(s.values(),[160,200,120]); assert.equal(s.root.classList.contains('resizing-table'),false);
  } finally {s.dispose();}
});

test('narrow columns resize, hidden tables wait for layout, and secondary pointers do nothing', () => {
  const s=setup([24,32,40]); try {
    const h=s.root.querySelector('.column-resizer'); h.dispatchEvent(s.pointer('pointerdown',24,{isPrimary:false}));
    assert.equal(s.saved.size,0);
    h.dispatchEvent(s.pointer('pointerdown',24)); h.dispatchEvent(s.pointer('pointermove',30));
    assert.deepEqual(s.values(),[48,48,48]); h.dispatchEvent(s.pointer('pointercancel',30));
    assert.equal(s.root.classList.contains('resizing-table'),false);
    s.render(); s.root.querySelector('th').getBoundingClientRect=()=>({width:0});
    s.root.querySelector('.column-resizer').dispatchEvent(s.pointer('pointerdown',20));
    assert.equal(s.root.classList.contains('resizing-table'),false);
  } finally {s.dispose();}
});
