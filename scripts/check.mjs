import { readFile, readdir, access, stat } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { load } from 'cheerio';
import MarkdownIt from 'markdown-it';
process.chdir(fileURLToPath(new URL('../',import.meta.url)));
async function walk(dir) {return (await Promise.all((await readdir(dir,{withFileTypes:true})).filter(x=>x.name!=='.DS_Store').map(x=>x.isDirectory()?walk(path.join(dir,x.name)):path.join(dir,x.name)))).flat();}
const base=new URL('http://localhost/ns-designer/');
for(const file of (await walk('dist')).filter(p=>p.endsWith('.html'))) {
 const $=load(await readFile(file,'utf8'));
 const ids=$('[id]').map((_,e)=>$(e).attr('id')).get();
 assert.equal(new Set(ids).size,ids.length,`Duplicate IDs in ${file}`);
 for(const e of $('[href], [src]').toArray()) for(const attr of ['href','src']) {
  const raw=$(e).attr(attr); if(!raw || /^(https?:|mailto:|data:)/.test(raw)) continue;
  const url=new URL(raw,new URL(file.slice(5),base));
  assert(url.pathname.startsWith(base.pathname),`Escaped Pages prefix: ${raw}`);
  const target='dist/'+decodeURIComponent(url.pathname.slice(base.pathname.length));
  assert((await stat(target)).isFile(),`Published link must resolve to a file: ${raw}`);
  if(url.hash && target.endsWith('.html')) {
   const doc=load(await readFile(target,'utf8'));
   assert(doc('[id]').toArray().some(e=>doc(e).attr('id')===decodeURIComponent(url.hash.slice(1))),`Missing anchor ${raw} in ${file}`);
  }
 }
}
for(const file of await walk('exports')) assert((await readFile(file)).equals(await readFile(file.replace(/^exports\//,'dist/downloads/'))),`Download differs: ${file}`);
for(const side of ['left','right']) {
 const dir=`hardware/pcb/${side}`;
 for(const f of [`${dir}/fp-lib-table`,`${dir}/sym-lib-table`,`${dir}/${side}.kicad_pcb`,...(await walk('hardware/pcb/lib')).filter(p=>p.endsWith('.kicad_mod'))]) {
  const text=await readFile(f,'utf8');
  for(const match of text.matchAll(/\$\{KIPRJMOD\}\/([^"\n]+)/g)) await access(path.resolve(dir,match[1]));
  assert(!text.includes('/Users/'),`Machine-local path in ${f}`);
 }
}
for(const side of ['tray','enclosed']) {
 const name=side==='tray'?'keyboard':'keyboard-enclosed';
 const buf=await readFile(`dist/downloads/models/${side}/${name}.glb`);
 assert.equal(buf.toString('utf8',0,4),'glTF');
}
const markdown=new MarkdownIt({html:true});
for(const file of ['README.md',...(await Promise.all(['buildbook','hardware','references','exports','firmware'].map(walk))).flat().filter(p=>p.endsWith('.md'))]) {
 const $=load(markdown.render(await readFile(file,'utf8')));
 for(const e of $('[href], [src]').toArray()) {
  const url=$(e).attr('href') || $(e).attr('src');
  if(!url || /^(https?:|mailto:|#)/.test(url)) continue;
  await access(path.resolve(path.dirname(file),url.split('#')[0]));
 }
}
console.log('Checked Pages-prefix links/anchors, download bytes, GLBs, project-relative KiCad references, and repository Markdown links.');
