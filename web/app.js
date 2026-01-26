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
    <div class="score-badge">
       <h3>${(scores.citation_score || {}).score || 0}/1</h3>
       <div class="label">Citation Credibility</div>
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
      <div class="metric-name">Citation Count</div>
      <div class="metric-val">${(scores.citation_score || {}).count || 0}</div>
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

  // 5. Feedback Loop
  const feedbackDiv = document.createElement('div');
  feedbackDiv.className = 'feedback-section';
  feedbackDiv.style.textAlign = 'center';
  feedbackDiv.style.marginTop = '24px';
  feedbackDiv.innerHTML = `
    <p style="color:#94a3b8;font-size:13px;margin-bottom:10px;">Is this result accurate?</p>
    <button class="btn" style="border:1px solid #10b981;color:#10b981;margin-right:8px;" onclick="sendFeedback(true, '${data.file}')">Yes, Accurate</button>
    <button class="btn" style="border:1px solid #ef4444;color:#ef4444;" onclick="sendFeedback(false, '${data.file}')">No, Inaccurate</button>
  `;
  result.appendChild(feedbackDiv);
}

// --- Feedback Logic ---
async function sendFeedback(isAccurate, filepath) {
  try {
    const filename = filepath ? filepath.split(/[\\/]/).pop() : 'unknown';
    const resp = await fetch('/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, is_accurate: isAccurate })
    });
    const res = await resp.json();
    alert(res.message);
  } catch (e) {
    console.error(e);
    alert('Failed to send feedback.');
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

// --- Navigation Logic ---
const navBtns = document.querySelectorAll('.nav-btn');
const pages = document.querySelectorAll('.page-section');

navBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    // Switch tabs
    navBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Switch pages
    const targetId = btn.getAttribute('data-target');
    pages.forEach(p => {
      if (p.id === targetId) {
        p.style.display = 'block';
        if (targetId === 'activity-page') loadActivityPage();
      } else {
        p.style.display = 'none';
      }
    });
  });
});

// --- Activity Dashboard Logic ---
let activityChart = null;

function loadActivityPage() {
  const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');

  // 1. Update Stats
  document.getElementById('totalScans').innerText = history.length;
  if (history.length > 0) {
    const avg = history.reduce((sum, h) => sum + (h.finalScore || 0), 0) / history.length;
    document.getElementById('avgAiScore').innerText = Math.round(avg * 100) + '%';
  } else {
    document.getElementById('avgAiScore').innerText = '0%';
  }

  // 2. Render Full List
  const list = document.getElementById('fullHistory');
  list.innerHTML = '';
  if (history.length === 0) {
    list.innerHTML = '<div style="text-align:center;color:#94a3b8;padding:20px;">No activity yet. Scan a document!</div>';
  } else {
    history.forEach(item => {
      const row = document.createElement('div');
      row.className = 'hist-row';
      const scoreColor = (item.finalScore || 0) > 0.5 ? '#fca5a5' : '#6ee7b7';
      row.innerHTML = `
        <div class="hist-info">
           <div class="hist-file">${item.filename}</div>
           <div class="hist-date">${item.date}</div>
        </div>
        <div class="hist-score" style="color:${scoreColor}">${Math.round((item.finalScore || 0) * 100)}% Risk</div>
      `;
      list.appendChild(row);
    });
  }

  // 3. Render Chart
  const ctx = document.getElementById('activityChart').getContext('2d');
  if (activityChart) activityChart.destroy();

  // Prepare data (last 10 scans reversed)
  const recentHist = history.slice(0, 10).reverse();
  const labels = recentHist.map((h, i) => `Scan ${i + 1}`);
  const dataPoints = recentHist.map(h => (h.finalScore || 0) * 100);

  activityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'AI Probability (%)',
        data: dataPoints,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#60a5fa'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#e2e8f0',
          bodyColor: '#e2e8f0',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' }
        },
        x: {
          grid: { display: false },
          ticks: { display: false } // hide x labels for cleaner look
        }
      }
    }
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
