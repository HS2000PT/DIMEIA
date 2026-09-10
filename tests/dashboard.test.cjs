// Unit tests of asynchronous ownership and caching, without a browser or network.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../web/assets/dashboard.js'),'utf8');

function setup(fetch) {
  const nodes=new Map();
  const element=()=>({innerHTML:'',textContent:'',className:'',hidden:false,value:'',
    setAttribute(){},addEventListener(){},querySelectorAll(){return [];},
    querySelector(){return element();},scrollIntoView(){},classList:{toggle(){}}});
  const context=vm.createContext({fetch,AbortController,URL,URLSearchParams,console,
    setTimeout(){return 1;},clearTimeout(){},
    matchMedia:()=>({matches:false,addEventListener(){}}),
    document:{hidden:false,querySelector(s){if(!nodes.has(s))nodes.set(s,element());return nodes.get(s);},
      querySelectorAll:()=>[],addEventListener(){}},
    window:{addEventListener(){}},location:{href:'http://localhost/'},history:{replaceState(){}}});
  vm.runInContext(source.replace('void refresh();void carregarFeed();pollTimer=setTimeout(poll,30000);',''),context);
  return {context,run:s=>vm.runInContext(s,context)};
}
const response=value=>({ok:true,json:async()=>value});

test('concurrent fetches share one request; resolved values are cached',async()=>{
  let finish,calls=0;
  const x=setup(()=>{calls++;return new Promise(r=>finish=r);});
  const a=x.run('json("/example")'),b=x.run('json("/example")');
  finish(response({value:42}));
  assert.equal((await a).value,42);await b;
  await x.run('json("/example")');assert.equal(calls,1);
});

test('a failed fetch can be retried',async()=>{
  let calls=0;
  const x=setup(async()=>++calls===1?{ok:false,status:503}:response({ok:true}));
  await assert.rejects(x.run('json("/example")'));
  assert.equal((await x.run('json("/example")')).ok,true);
  assert.equal(calls,2);
});

test('late company response cannot overwrite the newer selection',async()=>{
  const finish={};
  const x=setup(url=>new Promise(r=>finish[url]=r));
  x.run('S.visao={rows:[{ticker:"AAPL"},{ticker:"MSFT"}]}; pintarDetalhe=()=>{}; companyAlerts=async()=>{};');
  const old=x.run('abrirEmpresa("AAPL")'),recent=x.run('abrirEmpresa("MSFT")');
  finish['/api/asset/MSFT'](response({ticker:'MSFT'}));await recent;
  finish['/api/asset/AAPL'](response({ticker:'AAPL'}));await old;
  assert.equal(x.run('S.asset.ticker'),'MSFT');
});

test('chart disposal releases both charts and resize observers exactly once',()=>{
  const x=setup();
  x.run('var released=0; S.grafico={remove(){released++;}};S.graficoZ={remove(){released++;}};S.obs={disconnect(){released++;}};S.obsZ={disconnect(){released++;}};disposeCharts();disposeCharts();');
  assert.equal(x.run('released'),4);
});

test('polling does not start network work while hidden',async()=>{
  let calls=0;
  const x=setup(async()=>{calls++;return response({});});
  x.run('document.hidden=true');await x.run('poll()');assert.equal(calls,0);
});

test('untrusted links are escaped and only HTTP(S) links remain clickable',()=>{
  const x=setup();
  assert.equal(x.run('comLigacoes(esc(\'<a href="javascript:alert(1)">source</a>\'))'),'source');
  const link=x.run('comLigacoes(esc(\'<a href="https://example.com?a=1&b=2">source</a>\'))');
  assert.match(link,/href="https:\/\/example.com\?a=1&amp;b=2"/);
  assert.match(link,/noopener noreferrer nofollow/);
});
