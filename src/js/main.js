import { renderSolarField, solarAltitude } from '../astronomy/solar-field.js';
import { getSpaEvents, getSpaPosition } from '../astronomy/solar-spa.js';

(() => {
  const VIEWBOX = { width: 3025.3333, height: 2137.3333 };
  const UTC_OFFSET = 8 * 60 * 60 * 1000;
  const app = document.querySelector('.app-shell');
  const mapImage = document.querySelector('.map-image');
  const southSeaImage = document.querySelector('.south-sea-layer');
  if (southSeaImage) southSeaImage.src = 'assets/map/svg/south-sea-presentation.svg';
  const terrain = document.querySelector('#terrainVisualLayer');
  const solar = document.querySelector('#solarFieldLayer');
  const cityLayer = document.querySelector('#cityLayer');
  const analysis = document.querySelector('#analysisPanel');
  const compare = document.querySelector('#comparePanel');
  const astronomy = document.querySelector('#astronomyPanel');
  const hint = document.querySelector('#selectionHint');
  const fallback = [
    ['哈尔滨','interior',2293.3535,478.5389,126.535,45.8028],['乌鲁木齐','interior',789.5632,547.7053,87.6168,43.8256],['拉萨','interior',771.3615,1376.7095,91.1408,29.6456],['北京','capital',1958.1115,860.7744,116.4047,39.9042],['西安','interior',1630.4811,1202.9661,108.9398,34.3416],['成都','interior',1404.7802,1397.5587,104.0665,30.5723],['武汉','interior',1870.7434,1397.5587,114.3055,30.5928],['上海','coast',2231.1368,1342.9536,121.4737,31.2304],['广州','coast',1856.1821,1823.4782,113.2644,23.1291],['台北','island',2271.1805,1683.4906,121.5654,25.033],['海口','island',1699.6476,2011.121,110.1999,20.0442],['漠河','border',2121.9267,110.8648,122.5376,52.97],['抚远','border',2580.6092,289.2414,134.2957,48.367],['喀什','border',243.5125,656.9155,75.9897,39.4704],['曾母暗沙','island',2755.3454,2043.2222,112.2963,3.8329]
  ].map(([name,role,x,y,longitude,latitude]) => ({name,role,x,y,longitude,latitude}));
  const state = { points: [], selected: [], userSelected: false, minute: 300, season: 'summer-solstice', date: '2026-06-21', mode: 'dawn-progress', playing: false, timer: null };
  const $ = (s) => document.querySelector(s);

  function ensureStageMarkup() {
    const list = astronomy?.querySelector('.stage-list');
    if (!list) return;
    const stageKeys = ['astronomical', 'nautical', 'civil', 'sunrise', 'noon', 'sunset'];
    [...list.children].forEach((item, index) => { if (stageKeys[index]) item.dataset.stage = stageKeys[index]; });
    const extra = [
      ['正午', 'stageNoon', '太阳高度角达到当日峰值'],
      ['日落', 'stageSunset', '太阳中心约 -0.833°'],
    ];
    extra.forEach(([label, id, note]) => {
      if (document.getElementById(id)) return;
      const item = document.createElement('div');
      item.innerHTML = `<span>${label}</span><b id="${id}">--:--</b><small>${note}</small>`;
      list.append(item);
    });
    if (!astronomy.querySelector('.stage-summary')) {
      const summary = document.createElement('div');
      summary.className = 'stage-summary';
      summary.setAttribute('aria-label', '阶段摘要');
      [['民用晨光', 'stageSummaryCivil', 'civil'], ['日出', 'stageSummarySunrise', 'sunrise'], ['正午', 'stageSummaryNoon', 'noon'], ['日落', 'stageSummarySunset', 'sunset']].forEach(([label, id, key]) => {
        const item = document.createElement('div');
        item.dataset.stage = key;
        item.innerHTML = `<i class="stage-summary-icon" aria-hidden="true"></i><span>${label}</span><b id="${id}">--:--</b>`;
        summary.append(item);
      });
      astronomy.append(summary);
    }
  }

  function ensureCompareDetails() {
    if (!compare || compare.querySelector('.mini-curve')) return;
    const difference = compare.querySelector('.difference');
    if (difference) {
      const curve = document.createElement('div');
      curve.className = 'mini-curve';
      curve.setAttribute('aria-label', '早晚关系');
      curve.innerHTML = '<span>早</span><div class="curve-line"><i></i></div><span>晚</span>';
      difference.after(curve);
    }
    const details = compare.querySelector('.detail-grid');
    if (details) {
      const heading = document.createElement('div');
      heading.className = 'detail-heading';
      heading.innerHTML = '<span>更多信息</span><b id="detailHeadingNames"></b>';
      details.before(heading);
    }
  }

  function ensureOverview() {
    const summary = document.querySelector('.side-summary');
    if (!summary || !compare || summary.parentElement === compare) return;
    const latest = document.createElement('span');
    latest.innerHTML = '日出最晚 <b id="summaryLatest">--</b>';
    summary.append(latest);
    summary.classList.add('overview-inline');
    compare.append(summary);
  }

  function syncDetailHeading() {
    const label = $('#detailHeadingNames');
    if (!label) return;
    const a = state.points.find(p=>p.name===state.selected[0]) || state.points.find(p=>p.name==='北京') || fallback[3];
    const b = state.points.find(p=>p.name===state.selected[1]) || state.points.find(p=>p.name==='乌鲁木齐') || fallback[1];
    label.textContent = `（${a.name} / ${b.name}）`;
  }

  function migrateSeasonControls() {
    const rail = document.querySelector('.side-rail');
    const seasons = document.querySelector('.season-cards');
    const modes = document.querySelector('.mode-switcher');
    const selection = document.querySelector('#selectionHint');
    if (!rail) return;
    if (seasons) {
      seasons.classList.add('season-controls-rail');
      rail.prepend(seasons);
    }
    if (modes) {
      modes.classList.add('mode-controls-rail');
      rail.insertBefore(modes, rail.querySelector('.sunrise-ruler') || rail.firstChild);
    }
    if (selection) {
      selection.classList.add('selection-status-rail');
      rail.insertBefore(selection, rail.querySelector('.sunrise-ruler') || rail.lastChild);
    }
  }

  function syncSelectionHint() {
    if (!hint) return;
    const [a, b] = state.selected;
    if (state.mode === 'astronomy-stage') {
      hint.textContent = a && b ? `当前阶段参考：${a} / ${b}` : a ? `当前分析城市：${a}` : '选择一座城市，开始比较';
      return;
    }
    if (!state.userSelected || !a) {
      hint.textContent = '选择一座城市，开始比较';
    } else if (b) {
      hint.textContent = `${a}与${b}对比中`;
    } else {
      hint.textContent = `${a}已选中，再选择一座城市进行对比`;
    }
  }

  const adapt = (p) => { const v = Array.isArray(p.pickedV) ? p.pickedV : [p.x,p.y]; const x=Number(v?.[0]), y=Number(v?.[1]), longitude=Number(p.longitudeDeg ?? p.longitude), latitude=Number(p.latitudeDeg ?? p.latitude); return p.name && [x,y,longitude,latitude].every(Number.isFinite) ? {...p,x,y,longitude,latitude,displayRole:p.role==='border'?'extreme-point':p.role} : null; };
  const bjtUtc = (minutes) => { const [y,m,d]=state.date.split('-').map(Number); return new Date(Date.UTC(y,m-1,d,0,minutes)-UTC_OFFSET); };
  const bjt = (date) => new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',hour:'2-digit',minute:'2-digit',hour12:false}).format(date);
  const solarEvent = (p,target) => { const events=getSpaEvents(state.date,p); const event=target===-.833?events.sunrise:target===-6?events.civilDawn:target===-12?events.nauticalDawn:events.astronomicalDawn; return event ? (event.getTime()-bjtUtc(0).getTime())/60000 : null; };
  const seasonDates = { 'spring-equinox': ['春分','2026-03-20'], 'summer-solstice': ['夏至','2026-06-21'], 'autumn-equinox': ['秋分','2026-09-23'], 'winter-solstice': ['冬至','2026-12-22'] };
  const clampPercent = (minutes) => Math.max(0, Math.min(100, ((minutes - 180) / 420) * 100));
  const clockText = (minutes) => { const d=bjtUtc(minutes); return bjt(d); };

  function syncMarkers() { const lr=cityLayer.getBoundingClientRect(), ir=mapImage.getBoundingClientRect(); if(!lr.width||!ir.width)return; const sr=VIEWBOX.width/VIEWBOX.height, br=ir.width/ir.height, scale=br>sr?ir.height/VIEWBOX.height:ir.width/VIEWBOX.width, ox=(ir.width-VIEWBOX.width*scale)/2, oy=(ir.height-VIEWBOX.height*scale)/2; cityLayer.querySelectorAll('.city-marker').forEach((m)=>{const p=m._point;m.style.left=`${ir.left-lr.left+ox+p.x*scale}px`;m.style.top=`${ir.top-lr.top+oy+p.y*scale}px`;m.classList.toggle('selected',state.selected.includes(m.dataset.name));}); }
  function placeMarkers(points) { cityLayer.replaceChildren(); points.filter(p=>!['三沙','曾母暗沙','黄岩岛'].includes(p.name)).forEach((p)=>{const m=document.createElement('button');m.type='button';m.className='city-marker';m.dataset.name=p.name;m.dataset.role=p.displayRole||p.role;m.setAttribute('aria-label',`选择${p.name}`);m.innerHTML='<span class="city-marker-pin" aria-hidden="true"></span><span class="city-marker-label"></span>';m.querySelector('.city-marker-label').textContent=p.name;m._point=p;m.addEventListener('click',()=>selectCity(p.name));cityLayer.append(m);});syncMarkers();}
  function selectCity(name) { if(!state.points.some(p=>p.name===name))return; state.userSelected=true; if(state.selected.length===2)state.selected=[name]; else if(!state.selected.includes(name))state.selected.push(name); if(state.selected.length===2)setMode('location-compare'); syncSelectionHint(); render(); }
  function updatePanel() { const a=state.points.find(p=>p.name===state.selected[0])||state.points.find(p=>p.name==='北京')||fallback[3], b=state.points.find(p=>p.name===state.selected[1])||state.points.find(p=>p.name==='乌鲁木齐')||fallback[1]; ['rulerCityOne','compareNameOne'].forEach(id=>{const n=$(`#${id}`);if(n)n.textContent=a.name;}); ['rulerCityTwo','compareNameTwo'].forEach(id=>{const n=$(`#${id}`);if(n)n.textContent=b.name;}); const ea=solarEvent(a,-.833), eb=solarEvent(b,-.833), ca=solarEvent(a,-6), cb=solarEvent(b,-6); const one=$('#sunriseOne'),two=$('#sunriseTwo'),diff=$('#sunriseDifference'); if(one)one.textContent=ea==null?'--:--':bjt(bjtUtc(ea));if(two)two.textContent=eb==null?'--:--':bjt(bjtUtc(eb));if(diff&&ea!=null&&eb!=null){const mins=Math.round(Math.abs(eb-ea));diff.textContent=`${Math.floor(mins/60)}小时${String(mins%60).padStart(2,'0')}分`;} [['altitudeOne',a],['altitudeTwo',b]].forEach(([id,p])=>{const n=$(`#${id}`);if(n){const position=getSpaPosition(bjtUtc(state.minute),p);n.textContent=position?`${position.altitudeDeg.toFixed(1)}°`:'--.-°';}}); ['longitudeOne','longitudeTwo'].forEach((id,i)=>{const n=$(`#${id}`);if(n)n.textContent=`${[a,b][i].longitude.toFixed(1)}°E`;}); [['localTimeOne',a],['localTimeTwo',b]].forEach(([id,p])=>{const n=$(`#${id}`);if(n)n.textContent=bjt(bjtUtc(state.minute-(p.longitude-120)*4));}); [['civilDawnOne',ca],['civilDawnTwo',cb]].forEach(([id,m])=>{const n=$(`#${id}`);if(n)n.textContent=m==null?'--:--':bjt(bjtUtc(m));}); const narrative=$('#rulerNarrative'); if(narrative){const risenA=solarAltitude(bjtUtc(state.minute),a.longitude,a.latitude)>=-.833, risenB=solarAltitude(bjtUtc(state.minute),b.longitude,b.latitude)>=-.833; narrative.textContent=risenA&&risenB?`此刻，${a.name}与${b.name}都已迎来日出。`:risenA?`此刻，${a.name}已经日出，${b.name}仍在等待晨光。`:risenB?`此刻，${b.name}已经日出，${a.name}仍在等待晨光。`:`此刻，${a.name}与${b.name}都在等待晨光。`; } }
  function syncDerivedUi() {
    const a=state.points.find(p=>p.name===state.selected[0])||state.points.find(p=>p.name==='北京')||fallback[3];
    const b=state.points.find(p=>p.name===state.selected[1])||state.points.find(p=>p.name==='乌鲁木齐')||fallback[1];
    const ea=solarEvent(a,-.833), eb=solarEvent(b,-.833);
    const set=(id,value)=>{const n=$(`#${id}`);if(n)n.textContent=value;};
    set('rulerSunriseOne',ea==null?'--:--':bjt(bjtUtc(ea))); set('rulerSunriseTwo',eb==null?'--:--':bjt(bjtUtc(eb)));
    const delta=ea!=null&&eb!=null?Math.round(Math.abs(eb-ea)):null; set('rulerDifference',delta==null?'--':`${Math.floor(delta/60)}小时${String(delta%60).padStart(2,'0')}分`);
    const reliable=state.points.filter(p=>p.role!=='border'&&!['三沙','曾母暗沙','黄岩岛'].includes(p.name));
    const reliableEvents=reliable.map(p=>({p,minute:solarEvent(p,-.833)})).filter(item=>item.minute!=null);
    const earliest=reliableEvents.reduce((best,item)=>!best||item.minute<best.minute?item:best,null);
    const latest=reliableEvents.reduce((best,item)=>!best||item.minute>best.minute?item:best,null);
    const spread=earliest&&latest?Math.round(latest.minute-earliest.minute):null;
    set('summaryDifference',spread==null?'--':`${Math.floor(spread/60)}小时${String(spread%60).padStart(2,'0')}分`);
    set('summaryEarliest',earliest?`${earliest.p.name} ${bjt(bjtUtc(earliest.minute))}`:'--'); set('summaryLatest',latest?`${latest.p.name} ${bjt(bjtUtc(latest.minute))}`:'--');
    set('timelineCityOne',`${a.name}日出 ${ea==null?'--:--':bjt(bjtUtc(ea))}`); set('timelineCityTwo',`${b.name}日出 ${eb==null?'--:--':bjt(bjtUtc(eb))}`);
    const mark=(id,m)=>{const n=$(`#${id}`);if(n)n.style.left=`${clampPercent(m??0)}%`;}; mark('markOne',ea); mark('markTwo',eb); const ratio=clampPercent(state.minute); const handle=$('#trackHandle'),progress=$('#trackProgress'); if(handle)handle.style.left=`${ratio}%`; if(progress)progress.style.right=`${100-ratio}%`; const scale=document.querySelector('.track-scale'); if(scale){const p1=clampPercent(ea??180),p2=clampPercent(eb??600);scale.style.setProperty('--event-one',`${p1}%`);scale.style.setProperty('--event-two',`${p2}%`);scale.style.setProperty('--current',`${ratio}%`);scale.classList.toggle('events-close',ea!=null&&eb!=null&&Math.abs(p1-p2)<13);scale.classList.toggle('current-close-one',ea!=null&&Math.abs(p1-ratio)<8);scale.classList.toggle('current-close-two',eb!=null&&Math.abs(p2-ratio)<8);}
    const coverage=state.points.filter(p=>p.role!=='border'&&solarAltitude(bjtUtc(state.minute),p.longitude,p.latitude)>=-6).length; set('summaryCoverage',`${(coverage/Math.max(1,state.points.filter(p=>p.role!=='border').length)*100).toFixed(1)}%`);
    const events = getSpaEvents(state.date, a);
    const eventText = (event) => event ? bjt(event) : '--:--';
    set('stageAstronomical',solarEvent(a,-18)==null?'--:--':bjt(bjtUtc(solarEvent(a,-18))));
    set('stageNautical',solarEvent(a,-12)==null?'--:--':bjt(bjtUtc(solarEvent(a,-12))));
    set('stageCivil',solarEvent(a,-6)==null?'--:--':bjt(bjtUtc(solarEvent(a,-6))));
    set('stageSunrise',eventText(events.sunrise));
    set('stageNoon',eventText(events.solarNoon));
    set('stageSunset',eventText(events.sunset));
    set('stageSummaryCivil',solarEvent(a,-6)==null?'--:--':bjt(bjtUtc(solarEvent(a,-6))));
    set('stageSummarySunrise',eventText(events.sunrise));
    set('stageSummaryNoon',eventText(events.solarNoon));
    set('stageSummarySunset',eventText(events.sunset));
    const season=seasonDates[state.season]; const seasonLabel=document.querySelector('.season-line span:first-child'); const dateLabel=document.querySelector('.season-line span:last-child'); if(seasonLabel)seasonLabel.textContent=season[0]; if(dateLabel)dateLabel.textContent=state.date.replaceAll('-','.');
  }
  function setMode(mode) { state.mode=mode;app.dataset.mode=mode;const open=mode!=='dawn-progress';analysis.setAttribute('aria-hidden',String(!open));compare.hidden=mode!=='location-compare';astronomy.hidden=mode!=='astronomy-stage';const summary=document.querySelector('.side-summary');if(summary){summary.hidden=mode!=='location-compare';summary.setAttribute('aria-hidden',String(mode!=='location-compare'));}$('#panelTitle').textContent=mode==='astronomy-stage'?'天文阶段':'地点对比';$('#panelIcon').textContent=mode==='astronomy-stage'?'◌':'⌘';document.querySelectorAll('.mode-switcher [data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));syncSelectionHint(); }
  function syncStageHighlight() {
    const a = state.points.find(p=>p.name===state.selected[0]) || state.points.find(p=>p.name==='北京') || fallback[3];
    const events = getSpaEvents(state.date, a);
    const minute = event => event ? (event.getTime() - bjtUtc(0).getTime()) / 60000 : null;
    const altitude = solarAltitude(bjtUtc(state.minute), a.longitude, a.latitude);
    const noon = minute(events.solarNoon), sunset = minute(events.sunset);
    const active = altitude < -18 ? 'astronomical' : altitude < -12 ? 'nautical' : altitude < -6 ? 'civil' : altitude < -.833 ? 'sunrise' : (noon != null && state.minute >= noon - 30 && state.minute <= noon + 30) ? 'noon' : (sunset != null && state.minute >= sunset - 30) ? 'sunset' : 'sunrise';
    document.querySelectorAll('.stage-list > div, .stage-summary > div').forEach(item => item.classList.toggle('stage-current', item.dataset.stage === active));
  }
  function renderRelief() { const parent=terrain.parentElement.getBoundingClientRect(), ir=mapImage.getBoundingClientRect();if(!ir.width)return;const dpr=Math.min(devicePixelRatio||1,1.25);terrain.style.left=`${ir.left-parent.left}px`;terrain.style.top=`${ir.top-parent.top}px`;terrain.style.width=`${ir.width}px`;terrain.style.height=`${ir.height}px`;terrain.width=Math.round(ir.width*dpr);terrain.height=Math.round(ir.height*dpr);const c=terrain.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,ir.width,ir.height);const g=c.createRadialGradient(ir.width*.25,ir.height*.5,0,ir.width*.25,ir.height*.5,Math.max(ir.width,ir.height)*.6);g.addColorStop(0,'rgba(30,91,137,.22)');g.addColorStop(1,'rgba(2,15,31,0)');c.fillStyle=g;c.fillRect(0,0,ir.width,ir.height); }
  function render() { syncMarkers();renderRelief();const ir=mapImage.getBoundingClientRect();if(ir.width)renderSolarField(solar,ir,bjtUtc(state.minute));syncDetailHeading();updatePanel();syncDerivedUi();syncStageHighlight();const clock=$('.clock-line');if(clock)clock.innerHTML=`${bjt(bjtUtc(state.minute))} <small>BJT</small>`;const current=$('#timelineCurrent');if(current)current.textContent=bjt(bjtUtc(state.minute)); }
  function setup() { document.querySelectorAll('.mode-switcher [data-mode]').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.mode==='location-compare'&&state.selected.length<2){state.selected=['北京','乌鲁木齐'];state.userSelected=true;}setMode(b.dataset.mode);updatePanel();syncDerivedUi();}));document.querySelectorAll('.season-cards [data-season]').forEach((button)=>{button.addEventListener('click',()=>{const season=seasonDates[button.dataset.season];if(!season)return;state.season=button.dataset.season;state.date=season[1];state.minute=300;document.querySelectorAll('.season-cards button').forEach((item)=>item.classList.toggle('active',item===button));const range=$('#timeRange');if(range)range.value=String(state.minute);render();});});$('#closePanel').addEventListener('click',()=>setMode('dawn-progress')); const shortcuts=['北京','乌鲁木齐','广州','哈尔滨','拉萨','海口'];const layer=$('#cityShortcuts');shortcuts.forEach(name=>{const b=document.createElement('button');b.type='button';b.dataset.city=name;b.textContent=name;if(!state.points.some(p=>p.name===name)){b.disabled=true;b.title='暂无经人工核验的 V 坐标';}layer.append(b);});layer.addEventListener('click',e=>{const b=e.target.closest('[data-city]');if(b&&!b.disabled)selectCity(b.dataset.city);}); let range=$('#timeRange');if(!range){range=document.createElement('input');range.id='timeRange';range.type='range';range.min=180;range.max=600;range.value=state.minute;range.className='time-range';$('.timeline-track-wrap').prepend(range);}range.addEventListener('input',()=>{state.minute=Number(range.value);render();});$('#playToggle').addEventListener('click',()=>{state.playing=!state.playing;$('#playToggle').textContent=state.playing?'Ⅱ':'▶';$('#playToggle').setAttribute('aria-pressed',String(state.playing));if(state.timer)clearInterval(state.timer);if(state.playing)state.timer=setInterval(()=>{state.minute=state.minute>=600?180:state.minute+1;range.value=state.minute;render();},180);}); }
  async function load() { try { const r=await fetch('assets/map/metadata/control-points.json',{cache:'no-store'}); const raw=(await r.json()).controlPoints||[]; return raw.map(adapt).filter(Boolean); } catch(e) { console.warn('Control points fetch failed; using audited fallback.',e); return fallback; } }
  load().then(points=>{state.points=points.length?points:fallback;placeMarkers(state.points);ensureStageMarkup();ensureCompareDetails();migrateSeasonControls();ensureOverview();setup();state.selected=[];state.userSelected=false;setMode('dawn-progress');render();});mapImage.addEventListener('load',render);window.addEventListener('resize',render,{passive:true});
})();
