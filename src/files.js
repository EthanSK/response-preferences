export function decodeText(bytes) {
  const text = new TextDecoder('utf-8', {fatal:true, ignoreBOM:true}).decode(bytes);
  if (text.includes('\0')) throw Error('Only UTF-8 text files are supported.');
  return text;
}

export async function writeIfUnchanged(handle, expected, replacement) {
  const disk = decodeText(await (await handle.getFile()).arrayBuffer());
  if (disk !== expected) throw Error('This file changed somewhere else. Download your edited copy, then open the current file.');
  const writable = await handle.createWritable();
  try {await writable.write(replacement); await writable.close();}
  catch (error) {await writable.abort().catch(() => {}); throw error;}
}
