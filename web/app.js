const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const result = document.getElementById('result');
const dropZone = document.getElementById('dropZone');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
function humanPct(v){ return Math.round(v*100); }

function showResult(data){
  result.innerHTML = '';
  const scores = data.scores || {};
  const box = document.createElement('div');
  box.className = 'scores';

  const ai = document.createElement('div'); ai.className='score-badge';
  ai.innerHTML = `<h3>${humanPct(scores.ai_score || 0)}%</h3><div class="muted">AI likelihood</div>`;
  box.appendChild(ai);

  const pl = document.createElement('div'); pl.className='score-badge';
  pl.innerHTML = `<h3>${humanPct(scores.plagiarism_score || 0)}%</h3><div class="muted">Plagiarism</div>`;
  box.appendChild(pl);

  const fin = document.createElement('div'); fin.className='score-badge';
  fin.innerHTML = `<h3>${humanPct((scores.final||{}).final_probability || 0)}%</h3><div class="muted">Combined</div>`;
  box.appendChild(fin);

  result.appendChild(box);
  const decision = document.createElement('div'); decision.className='decision';
  decision.textContent = `Decision: ${(scores.final||{}).decision || data.scores?.final?.decision || 'N/A'}`;
  result.appendChild(decision);
  if (data.matches && data.matches.length){
    const mcont = document.createElement('div'); mcont.className='matches';
    const mh = document.createElement('h4'); mh.textContent = 'Suspicious matches'; mcont.appendChild(mh);
    data.matches.forEach(m => {
      const it = document.createElement('div'); it.className='match-item'; it.textContent = m;
      mcont.appendChild(it);
    });
    result.appendChild(mcont);
  }
  // metadata and excerpt
  if (data.sections){
    const meta = document.createElement('div'); meta.style.marginTop='12px';
  const title = data.metadata?.title || '';
  meta.innerHTML = `<div style="opacity:0.8;margin-bottom:6px">File: ${title}</div>`;
  if (data.sections.abstract) meta.innerHTML += `<div style="font-style:italic;background:rgba(255,255,255,0.02);padding:8px;border-radius:6px">${data.sections.abstract}</div>`;
    result.appendChild(meta);
  }
}
async function analyzeFile(){
  const f = fileInput.files[0];
  if (!f) return;
  analyzeBtn.disabled = true;
  result.innerHTML = 'Analyzing...';
  const fd = new FormData(); fd.append('file', f);
  try{
    const resp = await fetch('/analyze', { method: 'POST', body: fd });
    if (!resp.ok){
      const err = await resp.json(); result.textContent = 'Error: '+(err.detail||JSON.stringify(err));
      return;
    }
    const data = await resp.json();
    showResult(data);
  }catch(e){ result.textContent = 'Request failed: '+e }
  finally{ analyzeBtn.disabled = false }
}

form.addEventListener('submit', (e)=>{ e.preventDefault(); analyzeFile(); });
clearBtn.addEventListener('click', ()=>{ fileInput.value=''; result.innerHTML=''; });
// drag and drop
['dragenter','dragover'].forEach(ev => dropZone.addEventListener(ev, (e)=>{e.preventDefault(); dropZone.classList.add('dragover')}));
['dragleave','drop'].forEach(ev => dropZone.addEventListener(ev, (e)=>{e.preventDefault(); dropZone.classList.remove('dragover')}));
dropZone.addEventListener('drop', (e)=>{
  const f = e.dataTransfer.files[0]; if(!f) return; fileInput.files = e.dataTransfer.files; analyzeFile();
});
const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const result = document.getElementById('result');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = fileInput.files[0];
  if (!f) return;
  const fd = new FormData();
  fd.append('file', f);
  result.textContent = 'Analyzing...';
  try {
    const resp = await fetch('/analyze', { method: 'POST', body: fd });
    if (!resp.ok) {
      const err = await resp.json();
      result.textContent = 'Error: ' + (err.detail || JSON.stringify(err));
      return;
    }
    const data = await resp.json();
    result.textContent = JSON.stringify(data.scores, null, 2) + '\n\nSummary:\n' + data.summary || JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = 'Request failed: ' + err;
  }
});
