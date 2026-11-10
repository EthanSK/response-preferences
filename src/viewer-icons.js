// Type icons for the shared document/code viewer, embedded by its builder and browser entry point.
// The favicon identifies the viewing mode, independent of the project or document branding.
const symbols = {
  markdown: {color: '#6d28d9', path: '<path d="M14 46V18L32 36L50 18V46" fill="none" stroke="white" stroke-width="7" stroke-linejoin="round"/>'},
  code: {color: '#075985', path: '<path d="m24 18-14 14 14 14m16-28 14 14-14 14" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'},
  text: {color: '#365caa', path: '<path d="M17 9h22l9 9v37H17Z" fill="white"/><path d="M25 29h15M25 37h15M25 45h10" stroke="#365caa" stroke-width="4" stroke-linecap="round"/>'}
};

export function viewerIcon(name) {
  const kind = /\.(md|markdown)$/i.test(name) ? 'markdown' : /\.(txt|log)$/i.test(name) ? 'text' : 'code';
  const {color, path} = symbols[kind];
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="13" fill="${color}"/>${path}</svg>`;
  return 'data:image/svg+xml,' + encodeURIComponent(svg);
}
