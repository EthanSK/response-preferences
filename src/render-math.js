// Bundled for installed skills: no npm install, network, or DOM at check time.
import katex from 'katex';
import fs from 'node:fs';

const expressions = JSON.parse(fs.readFileSync(0, 'utf8'));
if (!Array.isArray(expressions) || expressions.length > 2000) throw Error('Invalid batch');
const results = expressions.map(expression => {
  if (typeof expression !== 'string' || expression.length > 10000) return 'Expression exceeds validation limit';
  let denied = false;
  try {
    katex.renderToString(expression, {
      throwOnError: true, strict: 'ignore', maxExpand: 1000, maxSize: 20,
      trust: () => { denied = true; return false; },
    });
    return denied ? 'Unsupported trusted command' : null;
  } catch (error) {
    // Never echo an entire private reply in checker/hook diagnostics.
    return String(error.message).split(/ at position | at end of input/)[0].slice(0, 160);
  }
});
process.stdout.write(JSON.stringify(results));
