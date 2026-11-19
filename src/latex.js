// Render the explicit LaTeX delimiters used in replies before Markdown consumes their backslashes.
import katex from 'katex';

const delimiters = [
  {open: '\\(', close: '\\)', displayMode: false},
  {open: '\\[', close: '\\]', displayMode: true},
  {open: '$$', close: '$$', displayMode: true},
];

export function renderLatex(expression, displayMode = false) {
  if (expression.length > 10000) throw Error('Expression exceeds validation limit');
  let denied = false;
  const rendered = katex.renderToString(expression, {
    displayMode,
    throwOnError: true,
    strict: 'ignore',
    maxExpand: 1000,
    maxSize: 20,
    trust: () => { denied = true; return false; },
  });
  if (denied) throw Error('Unsupported trusted command');
  return rendered;
}

export function enableLatex(md) {
  md.inline.ruler.before('escape', 'explicit_latex', (state, silent) => {
    const delimiter = delimiters.find(({open}) => state.src.startsWith(open, state.pos));
    if (!delimiter) return false;

    const start = state.pos + delimiter.open.length;
    let end = state.src.indexOf(delimiter.close, start);
    while (end !== -1 && end + delimiter.close.length <= state.posMax) {
      let escapeStart = end;
      while (escapeStart > start && state.src[escapeStart - 1] === '\\') escapeStart--;
      if ((end - escapeStart) % 2 === 0) {
        const expression = state.src.slice(start, end);
        if (!expression.trim() || (!delimiter.displayMode && expression.includes('\n'))) return false;
        const next = end + delimiter.close.length;
        if (!silent) {
          const token = state.push('explicit_latex', '', 0);
          token.content = expression;
          token.meta = {displayMode: delimiter.displayMode, original: state.src.slice(state.pos, next)};
        }
        state.pos = next;
        return true;
      }
      end = state.src.indexOf(delimiter.close, end + 1);
    }
    return false;
  });

  md.renderer.rules.explicit_latex = (tokens, index) => {
    const {content, meta} = tokens[index];
    try {
      return renderLatex(content, meta.displayMode);
    } catch {
      // Preserve malformed or untrusted source as plain text, with no active links or HTML.
      return md.utils.escapeHtml(meta.original);
    }
  };
}
