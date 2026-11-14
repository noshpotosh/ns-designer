import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../dist/',import.meta.url));
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.glb':'model/gltf-binary','.json':'application/json','.csv':'text/csv','.zip':'application/zip'};
export function preview(port=8000) {
 return createServer(async(req,res)=>{
  try {
   const url=new URL(req.url,'http://localhost');
   if(url.pathname==='/' || url.pathname==='/ns-designer') {res.writeHead(302,{location:'/ns-designer/'}).end();return;}
   if(!url.pathname.startsWith('/ns-designer/')) throw Error('outside prefix');
   const rel=decodeURIComponent(url.pathname.slice('/ns-designer/'.length)) || 'index.html';
   const file=resolve(root,rel);
   if(!file.startsWith(resolve(root)+sep)) throw Error('outside root');
   const content=await readFile(file);
   res.writeHead(200,{'content-type':types[extname(file)]||'application/octet-stream'}).end(content);
  } catch {res.writeHead(404).end('Not found');}
 }).listen(port,'127.0.0.1');
}
if(process.argv[1]===fileURLToPath(import.meta.url)) preview(Number(process.env.PORT||8000)).on('listening',()=>console.log(`Preview: http://localhost:${process.env.PORT||8000}/ns-designer/`));
