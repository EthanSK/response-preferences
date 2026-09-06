import test from 'node:test';
import assert from 'node:assert/strict';
import {decodeText,writeIfUnchanged} from '../src/files.js';

function fakeFile(text,{failWrite=false}={}) {
  const record={text,writes:0,aborts:0,closed:0};
  const handle={async getFile(){return {arrayBuffer:async()=>new TextEncoder().encode(record.text)};},async createWritable(){return {async write(value){record.writes++;if(failWrite)throw Error('Disk full');record.pending=value;},async close(){record.closed++;record.text=record.pending;},async abort(){record.aborts++;}};}};
  return {record,handle};
}
test('save refuses external edits without opening a writer',async()=>{
  const {record,handle}=fakeFile('newer disk content');
  await assert.rejects(writeIfUnchanged(handle,'old content','my edit'),/changed somewhere else/);
  assert.equal(record.writes,0);assert.equal(record.text,'newer disk content');
});
test('successful save closes the write and preserves exact new bytes',async()=>{
  const {record,handle}=fakeFile('\ufeffold\r\n');
  await writeIfUnchanged(handle,'\ufeffold\r\n','\ufeffnew\r\n');
  assert.equal(record.text,'\ufeffnew\r\n');assert.equal(record.closed,1);
});
test('failed write aborts the transaction and never reports completion',async()=>{
  const {record,handle}=fakeFile('old',{failWrite:true});
  await assert.rejects(writeIfUnchanged(handle,'old','new'),/Disk full/);
  assert.equal(record.aborts,1);assert.equal(record.closed,0);assert.equal(record.text,'old');
});
test('binary and malformed UTF-8 are rejected; BOM is retained',()=>{
  assert.throws(()=>decodeText(new Uint8Array([255])));
  assert.throws(()=>decodeText(new Uint8Array([0])));
  assert.equal(decodeText(new TextEncoder().encode('\ufefftext')),'\ufefftext');
});
