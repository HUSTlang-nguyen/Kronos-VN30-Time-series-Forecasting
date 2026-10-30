/** Check the offline HTML in Chrome. Requires the existing frontend dev packages. */
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { mkdir, writeFile } from 'node:fs/promises';
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(resolve(here, '../../demo/frontend/package.json'));
const { chromium } = require('@playwright/test');
const output = resolve(here, '../../.cache/slides-qa');
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ channel:'chrome', headless:true });
const page = await browser.newPage({ viewport:{width:1440,height:900}, reducedMotion:'reduce' });
const errors=[], requests=[];
page.on('pageerror', e=>errors.push(e.message));
await page.context().route(/^https?:/, async route=>{ requests.push(route.request().url()); await route.abort(); });
const url = pathToFileURL(resolve(here, 'vn30-paper-ink.html')).href;
await page.goto(url);
await page.waitForFunction(()=>window.Reveal?.isReady());
await page.evaluate(()=>document.fonts.ready);
const setup = await page.evaluate(()=>({
  slides:Reveal.getSlides().length,
  vietnameseFont:document.fonts.check('400 30px "Be Vietnam Pro"','Dự báo giá mở cửa'),
  monoFont:document.fonts.check('400 30px "IBM Plex Mono"','123,456'),
  scrollView:Reveal.isScrollView(),
}));
if(setup.slides!==19 || !setup.vietnameseFont || !setup.monoFont || !setup.scrollView) throw Error(JSON.stringify(setup));
const content=await page.evaluate(()=>{
 const slides=Reveal.getSlides();
 const text=slides.map(s=>s.querySelector('.frame').innerText).join('\n');
 const words=['huấn luyện','trọng số','học sẵn','mã hóa','giải mã','lượng tử hóa','thăm dò','PC mới','mốc'];
 return {ids:slides.map(s=>s.id),forbiddenTerms:words.filter(w=>text.toLowerCase().includes(w.toLowerCase())),
         removedSections:slides.some(s=>s.id==='kiem-dinh'||s.id==='gioi-han'),
         removedConclusion:text.includes('Ưu tiên tiếp theo:'),
         clarifiedP90:text.includes('90% volatility train')&&text.includes('không bắt buộc là 10% test'),
         quantizeExample:text.includes('Ví dụ minh họa theo dấu'),
 };
});
const expectedIds=['mo-dau','cau-hoi','baseline-naive-ridge','baseline-arima-ets','cach-kronos-du-bao','cac-model','du-lieu','kiem-tra-du-lieu','quy-trinh','chon-checkpoint','q1-close','q2-kich-thuoc','tokenization-quantize','q2-luong-tu-hoa','q3-du-lieu','q4-khoang-bat-dinh','q4-thoi-gian','q4-folds','ket-luan'];
if(JSON.stringify(content.ids)!==JSON.stringify(expectedIds)||content.forbiddenTerms.length||content.removedSections||content.removedConclusion||!content.clarifiedP90||!content.quantizeExample)throw Error(JSON.stringify(content));
const nearest=()=>page.evaluate(()=>{
  const v=Reveal.getViewportElement(),center=v.getBoundingClientRect().top+v.clientHeight/2;
  return Reveal.getSlides().map((s,i)=>({i,d:Math.abs(s.getBoundingClientRect().top+s.getBoundingClientRect().height/2-center)})).sort((a,b)=>a.d-b.d)[0].i;
});
const center=async i=>{
  await page.evaluate(i=>{
    const v=Reveal.getViewportElement(),s=Reveal.getSlides()[i],b=s.getBoundingClientRect(),vb=v.getBoundingClientRect();
    v.scrollTo({top:v.scrollTop+b.top+b.height/2-vb.top-v.clientHeight/2,behavior:'instant'});
  },i);
  await page.waitForTimeout(70);
};
const layout=[];
for(let i=0;i<19;i++){
  await center(i);
  const row=await page.evaluate(i=>{
    const s=Reveal.getSlides()[i],b=s.querySelector('.body'),h=s.querySelector('h1,h2'),f=s.querySelector('.chrome-foot');
    const bounds=b.getBoundingClientRect();
    return {slide:i+1,title:h.innerText,overflowY:b.scrollHeight-b.clientHeight,overflowX:b.scrollWidth-b.clientWidth,
      bodyBottom:bounds.bottom,footerTop:f.getBoundingClientRect().top,
      headerOverflow:h.scrollWidth-h.clientWidth,
      page:s.querySelector('[data-page]').textContent,
      emptyNotes:!s.querySelector('aside.notes')?.textContent.trim(),
      outliers:[...b.children].filter(e=>e.getBoundingClientRect().bottom>bounds.bottom+2).map(e=>e.tagName),
    };
  },i);
  layout.push(row);
  await page.locator('.reveal .slides section').nth(i).screenshot({path:resolve(output,`slide-${String(i+1).padStart(2,'0')}.png`)});
}
await center(0);
await page.waitForTimeout(200);
await page.keyboard.press('Tab');
if(await nearest()!==1)throw Error('Tab did not advance one slide');
for(let i=0;i<5;i++)await page.keyboard.press('Tab');
if(await nearest()!==6)throw Error('Rapid Tab destination lost');
await page.keyboard.press('Shift+Tab');
if(await nearest()!==5)throw Error('Shift+Tab failed');
await center(18);await page.waitForTimeout(200);await page.keyboard.press('Tab');
if(await nearest()!==18)throw Error('Last slide wrapped');
const endProgress=await page.locator('.reading-progress').getAttribute('aria-valuenow');
await center(0);await page.waitForTimeout(200);await page.keyboard.press('Shift+Tab');
if(await nearest()!==0)throw Error('First slide wrapped');
const startProgress=await page.locator('.reading-progress').getAttribute('aria-valuenow');
await page.evaluate(()=>{location.hash='#/2';});await page.waitForTimeout(200);
if(await nearest()!==2)throw Error('Numeric hash failed');
await page.evaluate(()=>{location.hash='#/ket-luan';});await page.waitForTimeout(200);
if(await nearest()!==18)throw Error('ID hash failed');
await page.evaluate(()=>{location.hash='#/does-not-exist';});await page.waitForTimeout(200);
if(await nearest()!==0)throw Error('Invalid hash failed');
await center(9);await page.waitForTimeout(200);
await page.evaluate(()=>{const v=Reveal.getViewportElement();v.scrollTop+=v.clientHeight*.27;});await page.waitForTimeout(200);
const before=await nearest();await page.keyboard.press('Tab');
if(await nearest()!==before+1)throw Error('Tab after manual scroll used wrong origin');
const inputGuard=await page.evaluate(()=>{
 const input=document.createElement('input');document.body.appendChild(input);input.focus();
 const event=new KeyboardEvent('keydown',{key:'Tab',bubbles:true,cancelable:true});input.dispatchEvent(event);input.remove();return !event.defaultPrevented;
});
const modifierGuard=await page.evaluate(()=>{
 const event=new KeyboardEvent('keydown',{key:'Tab',ctrlKey:true,bubbles:true,cancelable:true});document.dispatchEvent(event);return !event.defaultPrevented;
});
const responsive=[];
for(const viewport of [{width:1024,height:768},{width:390,height:844}]){
  await page.setViewportSize(viewport);await page.waitForTimeout(250);await center(9);
  responsive.push(await page.evaluate(()=>({width:innerWidth,horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,slideWidth:Reveal.getSlides()[9].getBoundingClientRect().width,slideHeight:Reveal.getSlides()[9].getBoundingClientRect().height})));
  await page.screenshot({path:resolve(output,`viewport-${viewport.width}.png`)});
}
await page.setViewportSize({width:1440,height:900});
await page.goto(url);await page.waitForFunction(()=>window.Reveal?.isReady());await page.waitForTimeout(200);
if(await nearest()!==0)throw Error('Fresh open restored old scroll position');
const checkpointIndex=await page.evaluate(()=>Reveal.getSlides().findIndex(s=>s.id==='chon-checkpoint'));
await center(checkpointIndex);await page.waitForTimeout(200);
await page.keyboard.press('f');await page.waitForTimeout(350);
const fullscreen=await page.evaluate(()=>!!document.fullscreenElement);
if(fullscreen)await page.evaluate(()=>document.exitFullscreen());
await page.waitForTimeout(250);
const notesPopup=page.waitForEvent('popup',{timeout:10000});await page.keyboard.press('s');
const notes=await notesPopup;await notes.waitForLoadState('domcontentloaded');await notes.waitForTimeout(350);
await notes.waitForFunction(()=>document.body.innerText.includes('Checkpoint là bản lưu'),null,{timeout:4000});
const notesReady=true;
await notes.close();
const problems=layout.filter(r=>r.overflowY>3||r.overflowX>3||r.headerOverflow>3||r.outliers.length||r.bodyBottom>r.footerTop+2||r.emptyNotes);
const receipt={status:problems.length||errors.length||requests.length||!inputGuard||!modifierGuard||!fullscreen||!notesReady||responsive.some(r=>r.horizontalOverflow)?'needs_fix':'pass',...setup,
  offline:true,content,networkRequests:requests,pageErrors:errors,layout,problems,
  navigation:{tab:true,rapidTab:true,shiftTab:true,boundaries:true,numericHash:true,idHash:true,invalidHash:true,manualScroll:true,freshOpen:true,fullscreen,speakerNotes:notesReady,inputGuard,modifierGuard,startProgress,endProgress},responsive};
await writeFile(resolve(output,'verification.json'),JSON.stringify(receipt,null,2));
console.log(JSON.stringify({status:receipt.status,problems,errors,requests,setup,navigation:receipt.navigation,responsive},null,2));
if(process.argv.includes('--pdf')&&receipt.status==='pass'){
 const printPage=await browser.newPage({viewport:{width:1920,height:1080}});
 printPage.on('pageerror',e=>errors.push(e.message));
 await printPage.route(/^https?:/,route=>route.abort());
 await printPage.goto(url+'?print-pdf');
 await printPage.waitForFunction(()=>document.querySelectorAll('.pdf-page').length===19,{timeout:30000});
 await printPage.evaluate(()=>document.fonts.ready);
 await printPage.waitForTimeout(350);
 await printPage.pdf({path:resolve(here,'vn30-paper-ink.pdf'),printBackground:true,preferCSSPageSize:true,width:'1920px',height:'1080px',displayHeaderFooter:false,margin:{top:0,right:0,bottom:0,left:0}});
 console.log('PDF exported');
}
await browser.close();
if(receipt.status!=='pass')process.exitCode=1;
