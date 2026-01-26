const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const result = document.getElementById('result');
const dropZone = document.getElementById('dropZone');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const recentScansContainer = document.getElementById('recentScans');
const historyContainer = document.getElementById('historyContainer');

// Utility to format percentage
function fmtPct(val) {
  return Math.round((val || 0) * 100) + '%';
}

function getDecisionColor(decision) {
  const d = decision.toLowerCase();
  if (d.includes('accept')) return '#6ee7b7'; // green
  if (d.includes('reject')) return '#fca5a5'; // red
  return '#fbbf24'; // yellow
}

// Render the detailed result view
function showResult(data) {
  result.style.display = 'block';
  result.innerHTML = '';

  const scores = data.scores || {};
  const metrics = data.scores?.ai_score?.metrics || {}; // Depending on how we structure it in API response
  // Since api.py passes 'ai_result' (dict) to report, it should be under scores.ai_score if generate_report puts it there.
  // Wait, generate_report structure: scores: { ai_score: <dict>, ... }

  const aiScoreVal = typeof scores.ai_score === 'object' ? scores.ai_score.score : scores.ai_score;
  const aiMetrics = typeof scores.ai_score === 'object' ? scores.ai_score.metrics : { perplexity: '-', burstiness: '-' };

  const finalProb = (scores.final || {}).final_probability || 0;
  const decision = (scores.final || {}).decision || 'Unknown';

  // 1. Decision Banner
  const decisionColor = getDecisionColor(decision);
  const decisionBox = document.createElement('div');
  decisionBox.className = 'decision-box';
  decisionBox.style.borderLeftColor = decisionColor;
  decisionBox.innerHTML = `
    <div><span class="decision-label">Recommendation:</span><span class="decision-value" style="color:${decisionColor}">${decision}</span></div>
    <div style="font-size:12px;opacity:0.7">Combined Score: ${fmtPct(finalProb)}</div>
  `;
  result.appendChild(decisionBox);

  // 2. Score Cards
  const grid = document.createElement('div');
  grid.className = 'scores';

  // AI Score
  grid.innerHTML += `
    <div class="score-badge">
      <h3>${fmtPct(aiScoreVal)}</h3>
      <div class="label">AI Probability</div>
    </div>
    <div class="score-badge">
      <h3>${fmtPct(scores.plagiarism_score)}</h3>
      <div class="label">Plagiarism</div>
    </div>
  `;
  result.appendChild(grid);

  // 3. Advanced Metrics Grid
  const metricsGrid = document.createElement('div');
  metricsGrid.className = 'metrics-grid';
  metricsGrid.innerHTML = `
    <div class="metric-item">
      <div class="metric-name">Perplexity</div>
      <div class="metric-val">${aiMetrics.perplexity || 'N/A'}</div>
    </div>
    <div class="metric-item">
      <div class="metric-name">Burstiness</div>
      <div class="metric-val">${aiMetrics.burstiness || 'N/A'}</div>
    </div>
    <div class="metric-item">
      <div class="metric-name">Avg Sentence Len</div>
      <div class="metric-val">${aiMetrics.avg_sentence_len || 'N/A'}</div>
    </div>
     <div class="metric-item">
      <div class="metric-name">Filename</div>
      <div class="metric-val" style="font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${data.file ? data.file.split(/[\\/]/).pop() : 'Unknown'}</div>
    </div>
  `;
  result.appendChild(metricsGrid);

  // 4. Suspicious Matches (if any)
  if (data.matches && data.matches.length > 0) {
    const mDiv = document.createElement('div');
    mDiv.className = 'matches';
    mDiv.innerHTML = '<h4>Flagged Segments</h4>';
    data.matches.forEach(m => {
      const row = document.createElement('div');
      row.className = 'match-item';
      row.innerText = m;
      mDiv.appendChild(row);
    });
    result.appendChild(mDiv);
  }
}

// --- History Logic ---
function saveToHistory(data) {
  const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
  const summary = {
    id: Date.now(),
    date: new Date().toLocaleString(),
    filename: data.file ? data.file.split(/[\\/]/).pop() : 'doc.txt',
    finalScore: (data.scores?.final?.final_probability || 0),
    data: data // store full data for reload
  };
  history.unshift(summary);
  if (history.length > 10) history.pop(); // keep last 10
  localStorage.setItem('scanHistory', JSON.stringify(history));
  renderHistory();
}

function renderHistory() {
  const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
  if (history.length === 0) {
    historyContainer.style.display = 'none';
    return;
  }
  historyContainer.style.display = 'block';
  recentScansContainer.innerHTML = '';

  history.forEach(item => {
    const el = document.createElement('div');
    el.className = 'recent-item';
    el.innerHTML = `
      <div class="recent-header">
        <span class="recent-file" title="${item.filename}">${item.filename}</span>
        <span class="recent-score">${fmtPct(item.finalScore)} AI/Plag</span>
      </div>
      <div class="recent-date">${item.date}</div>
    `;
    el.onclick = () => {
      showResult(item.data);
      result.scrollIntoView({ behavior: 'smooth' });
    };
    recentScansContainer.appendChild(el);
  });
}

// --- 3D Effects ---
// Dynamically load Vanilla-Tilt for the 3D effect
(function loadTilt() {
  const script = document.createElement('script');
  script.src = "https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.0/vanilla-tilt.min.js";
  script.onload = () => {
    VanillaTilt.init(document.querySelector("#tiltCard"), {
      max: 5,
      speed: 400,
      glare: true,
      "max-glare": 0.2,
      gyroscope: true,
    });
  };
  document.head.appendChild(script);
})();

// --- Download Report Logic ---
const downloadAction = document.getElementById('downloadAction');
const downloadBtn = document.getElementById('downloadBtn');
let currentReportData = null;

downloadBtn.addEventListener('click', () => {
  if (!currentReportData) return;

  const data = currentReportData;
  const fileName = (data.file || 'report').split(/[\\/]/).pop().replace(/\./g, '_') + '_analysis_report.txt';

  const content = `
SCHOLARLY PAPER DETECTION REPORT
================================
Date: ${new Date().toLocaleString()}
File: ${data.file || 'Unknown'}

ANALYSIS SUMMARY
----------------
Recommendation: ${(data.scores.final || {}).decision || 'N/A'}
Combined Probability: ${fmtPct((data.scores.final || {}).final_probability)}

DETAILED SCORES
---------------
AI Likelihood: ${fmtPct(typeof data.scores.ai_score === 'object' ? data.scores.ai_score.score : data.scores.ai_score)}
Plagiarism Score: ${fmtPct(data.scores.plagiarism_score)}

METRICS
-------
Perplexity: ${(data.scores.ai_score.metrics || {}).perplexity || 'N/A'}
Burstiness: ${(data.scores.ai_score.metrics || {}).burstiness || 'N/A'}
Avg Sentence Length: ${(data.scores.ai_score.metrics || {}).avg_sentence_len || 'N/A'}

SUSPICIOUS SEGMENTS
-------------------
${(data.matches || []).length > 0 ? data.matches.join('\n\n') : 'None found.'}

--------------------------------
Generated by Scholarly Paper Detector
  `.trim();

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});


// --- Main Analysis Logic ---
async function analyzeFile() {
  const f = fileInput.files[0];
  if (!f) return;

  analyzeBtn.disabled = true;
  analyzeBtn.innerText = 'Processing...';
  dropZone.classList.add('scanning'); // Start animation
  result.style.display = 'block';
  downloadAction.style.display = 'none'; // hide previous button
  result.innerHTML = '<div style="text-align:center;padding:40px;color:rgba(255,255,255,0.6);font-style:italic">Running detailed analysis...<br><span style="font-size:12px;opacity:0.5">Please wait while we scan your document</span></div>';

  const fd = new FormData();
  fd.append('file', f);

  try {
    const resp = await fetch('/analyze', {
      method: 'POST',
      body: fd
    });

    if (!resp.ok) {
      const err = await resp.json();
      result.innerHTML = `<div style="color:#ef4444;text-align:center;padding:20px">Error: ${err.detail || 'Unknown error'}</div>`;
      return;
    }

    const data = await resp.json();
    currentReportData = data; // store for download
    showResult(data);
    downloadAction.style.display = 'block'; // show download button
    saveToHistory(data);

  } catch (e) {
    result.innerHTML = `<div style="color:#ef4444;text-align:center;padding:20px">Network Error: ${e.message}</div>`;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerText = 'Analyze';
    dropZone.classList.remove('scanning'); // Stop animation
  }
}

// --- Event Listeners ---
form.addEventListener('submit', (e) => {
  e.preventDefault();
  analyzeFile();
});

clearBtn.addEventListener('click', () => {
  fileInput.value = '';
  result.style.display = 'none';
  result.innerHTML = '';
});

// Drag & Drop
['dragenter', 'dragover'].forEach(ev => dropZone.addEventListener(ev, (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
}));
['dragleave', 'drop'].forEach(ev => dropZone.addEventListener(ev, (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
}));
dropZone.addEventListener('drop', (e) => {
  const f = e.dataTransfer.files[0];
  if (f) {
    fileInput.files = e.dataTransfer.files;
    analyzeFile();
  }
});

fileInput.addEventListener('change', () => {
  // Optional: Auto submit or just show selected file name?
  // For now just let user click analyze
  if (fileInput.files[0]) {
    const name = fileInput.files[0].name;
    document.querySelector('.drop-title').innerText = name;
  }
});

// Init
renderHistory();
