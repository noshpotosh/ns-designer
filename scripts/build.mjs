import { readFile, writeFile, mkdir, rm, cp, access, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import MarkdownIt from 'markdown-it';
import GithubSlugger from 'github-slugger';
import { load } from 'cheerio';

export const root = fileURLToPath(new URL('../', import.meta.url));
process.chdir(root);
const chapters = [
  ['overview','Overview'], ['model','3D model'], ['readiness','Build readiness'],
  ['00-requirements','Requirements'], ['01-layout','Layout & matrix'],
  ['02-pcb','PCB design'], ['03-firmware','Firmware'], ['04-case','Case'],
  ['05-assembly','Assembly'], ['bom','Parts list'], ['resources','Resources'],
].map(([file,title]) => ({file:`buildbook/chapters/${file}.md`, id:file.replace(/^\d+-/,''),title}));
const byFile = new Map(chapters.map(c => [c.file,c]));
const md = new MarkdownIt({ html:true });
const sourceURL = 'https://github.com/noshpotosh/ns-designer/blob/main/';
await rm('dist', {recursive:true,force:true});
await mkdir('dist', {recursive:true});
await cp('buildbook/assets','dist/assets',{recursive:true,filter: p => !p.endsWith('.DS_Store')});
await cp('buildbook/viewer','dist/viewer',{recursive:true});
await cp('exports','dist/downloads',{recursive:true,filter: p => !p.endsWith('.DS_Store')});
for (const name of ['style.css','app.js']) await cp(`buildbook/template/${name}`,`dist/${name}`);
const sections = [];
for (const chapter of chapters) {
  const tokens = md.parse(await readFile(chapter.file,'utf8'), {});
  const slugger = new GithubSlugger();
  for (let i=0;i<tokens.length;i++) {
    if (tokens[i].type !== 'heading_open') continue;
    const slug = slugger.slug(tokens[i+1].content.replace(/[`*]/g,''));
    tokens[i].attrSet('id',`${chapter.id}--${slug}`);
    const level=Math.min(6,Number(tokens[i].tag.slice(1))+1);
    tokens[i].tag=`h${level}`; tokens[i+2].tag=`h${level}`;
  }
  const $ = load(md.renderer.render(tokens,md.options,{}),null,false);
  for (const el of $('[href], [src]').toArray()) {
    for (const attr of ['href','src']) {
      const href=$(el).attr(attr);
      if (!href || /^(https?:|mailto:|data:)/.test(href)) continue;
      if(href.startsWith('#')) {
        // Raw overview links refer to whole chapters; Markdown fragments refer to this chapter.
        if (!chapters.some(c => '#'+c.id === href)) $(el).attr(attr,`#${chapter.id}--${href.slice(1)}`);
        continue;
      }
      const [file,fragment] = href.split('#');
      const resolved=path.posix.normalize(path.posix.join(path.posix.dirname(chapter.file),file));
      await access(resolved); // fail on stale source references before publishing
      const target=byFile.get(resolved);
      let url;
      if(target) url=`#${target.id}${fragment?'--'+fragment:''}`;
      else if((await stat(resolved)).isDirectory()) url=sourceURL.replace('/blob/', '/tree/')+resolved;
      else if(resolved.startsWith('buildbook/assets/')) url=resolved.replace('buildbook/assets/','assets/');
      else if(resolved.startsWith('buildbook/viewer/')) url=resolved.replace('buildbook/viewer/','viewer/');
      else if(resolved.startsWith('exports/') && !resolved.endsWith('.md')) url=resolved.replace('exports/','downloads/');
      else url=((await stat(resolved)).isDirectory() ? sourceURL.replace('/blob/', '/tree/') : sourceURL)+resolved;
      if(fragment && !target) url+='#'+fragment;
      $(el).attr(attr,url);
    }
  }
  $('table').wrap('<div class="table-scroll"></div>');
  sections.push(`<section id="${chapter.id}">${$.html()}</section>`);
}
const nav=chapters.map(c=>`<li><a href="#${c.id}">${md.utils.escapeHtml(c.title)}</a></li>`).join('\n');
const template=await readFile('buildbook/template/index.html','utf8');
await writeFile('dist/index.html',template.replace('{{navigation}}',nav).replace('{{chapters}}',sections.join('\n')));
await writeFile('dist/.nojekyll','');
console.log('Built dist/index.html, assets, viewer, and downloads.');
