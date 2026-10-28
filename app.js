'use strict';
const data=window.POSE_DATA||{poses:[],angles:[]};
const poses=data.poses;
const $=s=>document.querySelector(s);
const angleLabels={'front':'Frente','three-quarter':'Tres cuartos','side':'Perfil','back':'Espalda','high':'Picado'};
const categoryLabels={'standing':'De pie','seated':'Sentadas','upper-body':'Gestos','action':'Acción','standing-balance':'De pie y equilibrio','communication':'Comunicación','emotion':'Emoción','chair':'Silla','floor-seated':'Sentadas en el suelo','kneeling':'De rodillas','reclining':'Reclinadas','walking-steps':'Caminar y pasos','running-jumping':'Correr y saltar','climbing-crawling':'Trepar y gatear'};
const label=c=>categoryLabels[c]||c.replaceAll('-',' ');
let favorites=new Set();try{favorites=new Set(JSON.parse(localStorage.getItem('oruga-favorites')||'[]'));}catch{}
let state={query:'',category:'',favorites:false,angle:1,page:0};
let filtered=[],current=null,currentAngle=1,timerSeconds=60,timerRemaining=60,timerHandle=null,timerDeadline=null;
const pageSize=60;
const normalize=t=>String(t||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
function setSprite(el,p,index){el.style.backgroundImage=`url("${p.sprite}")`;const rows=p.spriteRows||1;el.style.backgroundSize=`500% ${rows*100}%`;el.style.backgroundPosition=`${index*25}% ${rows===1?50:(p.spriteRow||0)*100/(rows-1)}%`;}
function setThumb(el,p){const i=p.thumb.index;el.style.backgroundImage=`url("site-assets/thumbs/${String(p.thumb.sheet).padStart(3,'0')}.webp")`;el.style.backgroundSize='1000% 1000%';el.style.backgroundPosition=`${(i%10)*100/9}% ${Math.floor(i/10)*100/9}%`;}
function saveFavorites(){try{localStorage.setItem('oruga-favorites',JSON.stringify([...favorites]));}catch{}$('#favorites-count').textContent=favorites.size;}
function render(){
 filtered=poses.filter(p=>(!state.category||p.category===state.category)&&(!state.favorites||favorites.has(p.id))&&(!state.query||normalize([p.name,p.name_en,p.category,...(p.tags||[])].join(' ')).includes(normalize(state.query))));
 state.page=Math.min(state.page,Math.max(0,Math.ceil(filtered.length/pageSize)-1));
 const gallery=$('#gallery');gallery.replaceChildren();
 for(const p of filtered.slice(state.page*pageSize,(state.page+1)*pageSize)){
  const card=document.createElement('button');card.className='pose-card';card.type='button';card.setAttribute('aria-label',`Abrir ${p.name}`);
  const thumb=document.createElement('div');thumb.className='pose-thumb';if(state.angle===1&&p.thumb)setThumb(thumb,p);else setSprite(thumb,p,state.angle);
  const num=document.createElement('span');num.className='pose-number';num.textContent=String(poses.indexOf(p)+1).padStart(3,'0');thumb.append(num);
  if(favorites.has(p.id)){const heart=document.createElement('span');heart.className='pose-fav';heart.textContent='♥';thumb.append(heart);}
  const info=document.createElement('div');info.className='pose-info';const text=document.createElement('div');const h=document.createElement('h3');h.textContent=p.name;const sub=document.createElement('p');sub.textContent=`${label(p.category)} · 5 vistas`;text.append(h,sub);const arrow=document.createElement('span');arrow.textContent='↗';info.append(text,arrow);card.append(thumb,info);card.addEventListener('click',()=>openPose(p,state.angle));gallery.append(card);
 }
 $('#result-count').textContent=`${filtered.length} de ${poses.length} poses`;
 $('#empty').hidden=filtered.length>0;$('#page-status').textContent=filtered.length?`${state.page+1} / ${Math.ceil(filtered.length/pageSize)}`:'0 / 0';$('#previous').disabled=state.page===0;$('#next').disabled=(state.page+1)*pageSize>=filtered.length;
 $('#favorites').setAttribute('aria-pressed',String(state.favorites));saveFavorites();
}
function angleButtons(container,onClick,active){container.replaceChildren();data.angles.forEach((a,i)=>{const b=document.createElement('button');b.type='button';b.textContent=angleLabels[a];b.className=i===active?'active':'';b.setAttribute('aria-pressed',String(i===active));b.addEventListener('click',()=>onClick(i));container.append(b);});}
function openPose(p,index=1){current=p;currentAngle=index;$('#viewer-title').textContent=p.name;$('#viewer-category').textContent=label(p.category);$('#pose-code').textContent=p.id;$('#viewer-tags').replaceChildren(...(p.tags||[]).map(t=>{const s=document.createElement('span');s.textContent=t;return s;}));updateViewer();if(!$('#viewer').open)$('#viewer').showModal();}
function updateViewer(){setSprite($('#large-pose'),current,currentAngle);$('#angle-label').textContent=angleLabels[data.angles[currentAngle]];angleButtons($('#viewer-angles'),i=>{currentAngle=i;updateViewer();},currentAngle);$('#save-pose').textContent=favorites.has(current.id)?'♥ Pose guardada':'♡ Guardar pose';}
function randomPose(){const list=filtered.length?filtered:poses;if(list.length)openPose(list[Math.floor(Math.random()*list.length)],state.angle);}
function downloadBlob(blob,filename){const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(u),1500);}
$('#download-png').addEventListener('click',async()=>{if(!current)return;const button=$('#download-png');button.disabled=true;button.textContent='Preparando…';const p=current,i=currentAngle;try{const image=new Image();image.src=p.sprite;await image.decode();const canvas=document.createElement('canvas');canvas.width=p.width;canvas.height=p.height;canvas.getContext('2d').drawImage(image,i*p.width,(p.spriteRow||0)*p.height,p.width,p.height,0,0,p.width,p.height);const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));downloadBlob(blob,`${p.id}-${data.angles[i]}.png`);}catch{alert('No pudimos preparar la descarga. Abre la galería desde un servidor local o GitHub Pages.');}finally{button.disabled=false;button.textContent='Descargar PNG ↓';}});
$('#download-json').addEventListener('click',()=>{if(current){const{sprite,spriteRows,spriteRow,width,height,thumb,...pose}=current;downloadBlob(new Blob([JSON.stringify(pose,null,2)],{type:'application/json'}),`${current.id}.json`);}});
$('#save-pose').addEventListener('click',()=>{if(favorites.has(current.id))favorites.delete(current.id);else favorites.add(current.id);updateViewer();render();});
$('#search').addEventListener('input',e=>{state.query=e.target.value;state.page=0;render();});$('#category').addEventListener('change',e=>{state.category=e.target.value;state.page=0;render();});$('#favorites').addEventListener('click',()=>{state.favorites=!state.favorites;state.page=0;render();});
$('#reset-filters').addEventListener('click',()=>{state.query='';state.category='';state.favorites=false;state.page=0;$('#search').value='';$('#category').value='';render();});
$('#random').addEventListener('click',randomPose);$('#hero-random').addEventListener('click',randomPose);$('#previous').addEventListener('click',()=>{state.page--;render();$('#library').scrollIntoView();});$('#next').addEventListener('click',()=>{state.page++;render();$('#library').scrollIntoView();});
$('#close').addEventListener('click',()=>$('#viewer').close());$('#viewer').addEventListener('click',e=>{if(e.target===$('#viewer')){const r=$('#viewer').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('#viewer').close();}});
function movePose(step){const list=filtered.length?filtered:poses;const i=list.findIndex(p=>p.id===current.id);openPose(list[(Math.max(0,i)+step+list.length)%list.length],currentAngle);}
$('#prev-pose').addEventListener('click',()=>movePose(-1));$('#next-pose').addEventListener('click',()=>movePose(1));
document.addEventListener('keydown',e=>{if($('#viewer').open&&['ArrowLeft','ArrowRight'].includes(e.key)&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();currentAngle=(currentAngle+(e.key==='ArrowRight'?1:-1)+5)%5;updateViewer();}});
function displayTimer(){const s=Math.max(0,timerRemaining);$('#timer-display').textContent=`${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;}
function stopTimer(){clearInterval(timerHandle);timerHandle=null;$('#timer-toggle').textContent=timerRemaining===0?'Repetir':'Comenzar';}
$('.timer-options').addEventListener('click',e=>{const b=e.target.closest('[data-seconds]');if(!b)return;stopTimer();timerSeconds=Number(b.dataset.seconds);timerRemaining=timerSeconds;displayTimer();document.querySelectorAll('[data-seconds]').forEach(x=>x.classList.toggle('active',x===b));});
$('#timer-toggle').addEventListener('click',()=>{if(timerHandle){timerRemaining=Math.max(0,Math.ceil((timerDeadline-Date.now())/1000));stopTimer();displayTimer();return;}if(!timerRemaining)timerRemaining=timerSeconds;timerDeadline=Date.now()+timerRemaining*1000;$('#timer-toggle').textContent='Pausar';timerHandle=setInterval(()=>{timerRemaining=Math.max(0,Math.ceil((timerDeadline-Date.now())/1000));displayTimer();if(timerRemaining===0)stopTimer();},200);});$('#viewer').addEventListener('close',stopTimer);
[...new Set(poses.map(p=>p.category))].sort((a,b)=>label(a).localeCompare(label(b),'es')).forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=label(c);$('#category').append(o);});
// Use a named callback to keep angle controls compatible with strict mode.
function chooseAngle(i){state.angle=i;render();angleButtons($('#angle-buttons'),chooseAngle,i);}angleButtons($('#angle-buttons'),chooseAngle,state.angle);
$('#count-poses').textContent=poses.length;if(poses.length)setSprite($('#hero-figure'),poses.find(p=>p.id==='action-balance')||poses[Math.min(5,poses.length-1)],1);render();displayTimer();
