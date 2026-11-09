const form=document.querySelector('#form');
const gallery=document.querySelector('#gallery');
const statusEl=document.querySelector('#status');
const generate=document.querySelector('#generate');
const shuffle=document.querySelector('#shuffle');
const sentence=document.querySelector('#sentence');
const eras=['1998','2003','2007','2011','1987','1994','2015','2001'];
const traces=['personal blog photograph','family snapshot','old web diary','amateur digital camera','travel journal photo','personal photo archive','local newspaper photograph','scanned photo album'];
const places=['Kyoto','Detroit','London','Melbourne','Providence','Osaka','Berlin','Toronto','Shanghai','Glasgow'];
let cards=[];let run=0;
const pick=a=>a[Math.floor(Math.random()*a.length)];
function makeSeed(){return `${pick(traces)} ${pick(eras)} ${pick(places)}`;}
function words(){return (sentence.value.match(/[\p{L}\p{N}]+(?:['’\-][\p{L}\p{N}]+)*/gu)||[]).slice(0,24);}
function setBusy(v){generate.disabled=v;shuffle.disabled=v;}
function render(){gallery.replaceChildren();cards.forEach((card,i)=>{
 const el=document.createElement('article');el.className='item';
 const pic=document.createElement('div');pic.className='picture';
 if(card.loading){pic.textContent='Searching…';pic.classList.add('empty');}
 else if(card.image){const img=document.createElement('img');img.src=card.image.thumb;img.alt=card.image.title||`Found image for ${card.word}`;img.loading='lazy';img.referrerPolicy='no-referrer';img.onerror=()=>{pic.textContent='Image unavailable';pic.classList.add('empty');};pic.append(img);}
 else {pic.textContent='';}
 const meta=document.createElement('div');meta.className='meta';
 const word=document.createElement('span');word.className='word';word.textContent=card.word;
 const actions=document.createElement('span');actions.className='actions';
 const btn=document.createElement('button');btn.textContent='↻';btn.title='Find another image';btn.setAttribute('aria-label',`Find another image for ${card.word}`);btn.disabled=card.loading;btn.onclick=()=>reload(i,run);
 actions.append(btn);
 if(card.image){const a=document.createElement('a');a.href=card.image.source;a.target='_blank';a.rel='noopener noreferrer';a.textContent=[card.image.creator,card.image.license].filter(Boolean).join(' · ')||'source ↗';actions.append(a);}
 meta.append(word,actions);
 const sub=document.createElement('div');sub.className='small';sub.textContent=card.query||'';
 el.append(pic,meta,sub);gallery.append(el);
 });}
async function reload(i,current){const card=cards[i];if(!card)return;card.loading=true;card.error='';card.image=null;card.query='';render();
 const seed=makeSeed();
 try{const r=await fetch(`/api/images?word=${encodeURIComponent(card.word)}&seed=${encodeURIComponent(seed)}`);const data=await r.json();if(!r.ok)throw Error(data.error||'Search failed');if(current!==run)return;card.query=data.query;const images=data.results||[];card.image=images.length?pick(images):null;if(!card.image)card.error='No results';}
 catch(e){if(current!==run)return;card.error='';}
 finally{if(current===run){card.loading=false;render();}}}
async function all(){const w=words().sort(()=>Math.random()-.5).slice(0,3);if(!w.length){statusEl.textContent='Enter some text first.';return;}run++;const current=run;cards=w.map(word=>({word,loading:true,image:null,error:'',query:''}));render();setBusy(true);statusEl.textContent=`Searching for ${w.length} words…`;
 // Small batches avoid flooding the provider with simultaneous requests.
 for(let i=0;i<cards.length;i+=3){await Promise.all(cards.slice(i,i+3).map((_,offset)=>reload(i+offset,current)));if(current!==run)return;statusEl.textContent=`Found ${Math.min(i+3,cards.length)} / ${cards.length} words`;}
 if(current===run){setBusy(false);statusEl.textContent='';shuffle.hidden=false;}}
form.addEventListener('submit',e=>{e.preventDefault();all();});shuffle.addEventListener('click',all);
