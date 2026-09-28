/** Add view-only column dividers; keep widths while the same document is rerendered. */
export function resizeTables(root, savedWidths) {
  let finishDrag = () => {};
  const document = root.ownerDocument;
  for (const [tableIndex, table] of [...root.querySelectorAll('table')].entries()) {
    const cells = [...(table.tHead?.rows[0]?.cells || [])];
    if (cells.length < 2) continue;
    const key = JSON.stringify([tableIndex, cells.map(cell => cell.textContent)]);
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    table.before(wrapper); wrapper.append(table);
    const group = document.createElement('colgroup');
    const columns = cells.map(() => group.appendChild(document.createElement('col')));
    table.prepend(group);
    let widths = savedWidths.get(key)?.slice();
    const handles = [];
    function apply() {
      table.style.tableLayout = 'fixed';
      table.style.width = widths.reduce((sum, width) => sum + width, 0) + 'px';
      columns.forEach((column, index) => { column.style.width = widths[index] + 'px'; });
      handles.forEach((handle, index) => {
        handle.setAttribute('aria-valuenow', String(Math.round(widths[index])));
        handle.setAttribute('aria-valuemax', String(Math.round(widths[index] + widths[index + 1] - 48)));
      });
    }
    function measure() {
      // Wait for pointer/keyboard input: a preview rendered in Edit mode has zero width.
      const measured = cells.map(cell => cell.getBoundingClientRect().width);
      if (!measured.every(width => width > 0)) return false;
      widths = measured.map(width => Math.max(48, width));
      return true;
    }
    function change(index, start, delta) {
      const bounded = Math.max(48 - start[index], Math.min(delta, start[index + 1] - 48));
      widths = start.slice(); widths[index] += bounded; widths[index + 1] -= bounded;
      savedWidths.set(key, widths.slice()); apply();
    }
    cells.slice(0, -1).forEach((cell, index) => {
      const handle = document.createElement('span');
      handle.className = 'column-resizer'; handle.tabIndex = 0;
      handle.setAttribute('role', 'separator'); handle.setAttribute('aria-orientation', 'vertical');
      handle.setAttribute('aria-label', cell.textContent.trim()); handle.setAttribute('aria-valuemin', '48');
      handles.push(handle); cell.append(handle);
      handle.addEventListener('pointerdown', event => {
        if (event.button !== 0 || !event.isPrimary) return;
        finishDrag(); if (!measure()) return;
        event.preventDefault();
        const start = widths.slice(), startX = event.clientX, pointer = event.pointerId;
        const previous = savedWidths.get(key)?.slice();
        handle.setPointerCapture(pointer); handle.focus();
        root.classList.add('resizing-table');
        const move = next => { if (next.pointerId === pointer) change(index, start, next.clientX - startX); };
        const stop = () => finishDrag();
        const escape = next => {
          if (next.key !== 'Escape') return;
          next.preventDefault(); widths = start; apply();
          if (previous) savedWidths.set(key, previous); else savedWidths.delete(key);
          finishDrag();
        };
        finishDrag = () => {
          handle.removeEventListener('pointermove', move); handle.removeEventListener('pointerup', stop);
          handle.removeEventListener('pointercancel', stop); handle.removeEventListener('lostpointercapture', stop);
          document.removeEventListener('keydown', escape); document.defaultView.removeEventListener('blur', stop);
          root.classList.remove('resizing-table');
          if (handle.hasPointerCapture(pointer)) handle.releasePointerCapture(pointer);
          finishDrag = () => {};
        };
        handle.addEventListener('pointermove', move); handle.addEventListener('pointerup', stop);
        handle.addEventListener('pointercancel', stop); handle.addEventListener('lostpointercapture', stop);
        document.addEventListener('keydown', escape); document.defaultView.addEventListener('blur', stop);
      });
      handle.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key) || !measure()) return;
        event.preventDefault();
        change(index, widths, (event.key === 'ArrowRight' ? 1 : -1) * (event.shiftKey ? 1 : 10));
      });
      handle.addEventListener('dblclick', () => {
        finishDrag(); savedWidths.delete(key); widths = undefined;
        table.style.removeProperty('width'); table.style.removeProperty('table-layout');
        columns.forEach(column => column.style.removeProperty('width'));
        handles.forEach(item => { item.removeAttribute('aria-valuenow'); item.removeAttribute('aria-valuemax'); });
      });
    });
    if (widths?.length === columns.length) apply();
  }
  return () => finishDrag();
}
