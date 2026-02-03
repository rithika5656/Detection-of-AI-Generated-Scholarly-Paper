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

  // 2. Score Cards (Grid)
  const grid = document.createElement('div');
  grid.className = 'scores';

  const humanScoreVal = 1.0 - aiScoreVal;

  // AI & Human Score
  grid.innerHTML += `
    <div class="score-badge">
      <h3 style="color:#f87171">${fmtPct(aiScoreVal)}</h3>
      <div class="label">AI Generated</div>
    </div>
    <div class="score-badge">
      <h3 style="color:#4ade80">${fmtPct(humanScoreVal)}</h3>
      <div class="label">Human Written</div>
    </div>
    <div class="score-badge">
       <h3>${(scores.citation_score || {}).score || 0}/1</h3>
       <div class="label">Citation Credibility</div>
    </div>
  `;
  result.appendChild(grid);

  // --- NEW: Scholarship Eligibility Card ---
  if (data.eligibility) {
    const elig = data.eligibility;
    const eBox = document.createElement('div');
    eBox.className = 'decision-box';
    // Style it distinctly
    eBox.style.marginTop = '20px';
    eBox.style.flexDirection = 'column';
    eBox.style.alignItems = 'flex-start';
    eBox.style.background = 'rgba(6, 182, 212, 0.1)';
    eBox.style.border = '1px solid rgba(6, 182, 212, 0.3)';

    const statusColor = elig.is_eligible ? '#4ade80' : '#f87171';
    const statusText = elig.is_eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE';

    let reasonsHtml = '';
    if (elig.reasons && elig.reasons.length > 0) {
      reasonsHtml = '<ul style="margin:10px 0 0 20px;font-size:13px;color:#cbd5e1;">' +
        elig.reasons.map(r => `<li>${r}</li>`).join('') +
        '</ul>';
    } else {
      reasonsHtml = '<div style="margin-top:10px;font-size:13px;color:#cbd5e1;">Meets all core criteria for scholarship consideration.</div>';
    }

    eBox.innerHTML = `
        <div style="width:100%;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:12px;text-transform:uppercase;color:#06b6d4;letter-spacing:1px;">Scholarship Status</span>
            <span style="font-size:16px;font-weight:700;color:${statusColor}">${statusText}</span>
        </div>
        <div style="width:100%;height:1px;background:rgba(6,182,212,0.2);"></div>
        ${reasonsHtml}
        <div style="margin-top:12px;font-size:12px;color:#94a3b8;">
            Data Integrity Score: <strong style="color:white">${Math.round(elig.integrity_score * 100)}/100</strong>
        </div>
      `;
    result.appendChild(eBox);
  }


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

// ==================== CHATBOT FUNCTIONALITY ====================

const chatbotToggle = document.getElementById('chatbotToggle');
const chatbotContainer = document.getElementById('chatbotContainer');
const chatbotClose = document.getElementById('chatbotClose');
const chatbotMessages = document.getElementById('chatbotMessages');
const chatbotInput = document.getElementById('chatbotInput');
const chatbotSend = document.getElementById('chatbotSend');
const chatSuggestions = document.getElementById('chatSuggestions');
const chatNotification = document.getElementById('chatNotification');

// Store analysis context for chatbot
let chatAnalysisContext = null;

// Format markdown-like text to HTML
function formatChatMessage(text) {
  return text
    // Bold text
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Headers
    .replace(/^### (.+)$/gm, '<h4 style="margin:8px 0 4px;font-size:13px;color:#94a3b8">$1</h4>')
    // Bullet points
    .replace(/^• (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, '<ul style="margin:8px 0;padding-left:16px;">$&</ul>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
}

// Add message to chat
function addChatMessage(text, isBot = true) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-message ${isBot ? 'bot' : 'user'}`;
  
  const avatar = document.createElement('div');
  avatar.className = 'chat-message-avatar';
  avatar.textContent = isBot ? '🤖' : '👤';
  
  const content = document.createElement('div');
  content.className = 'chat-message-content';
  content.innerHTML = isBot ? `<p>${formatChatMessage(text)}</p>` : text;
  
  msgDiv.appendChild(avatar);
  msgDiv.appendChild(content);
  chatbotMessages.appendChild(msgDiv);
  
  // Scroll to bottom
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
  const indicator = document.createElement('div');
  indicator.className = 'chat-message bot';
  indicator.id = 'typingIndicator';
  indicator.innerHTML = `
    <div class="chat-message-avatar">🤖</div>
    <div class="chat-message-content">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  chatbotMessages.appendChild(indicator);
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) indicator.remove();
}

// Send message to chatbot API
async function sendChatMessage(message) {
  if (!message.trim()) return;
  
  // Add user message
  addChatMessage(message, false);
  chatbotInput.value = '';
  chatbotSend.disabled = true;
  
  // Show typing indicator
  showTypingIndicator();
  
  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        analysis_context: chatAnalysisContext
      })
    });
    
    removeTypingIndicator();
    
    if (response.ok) {
      const data = await response.json();
      addChatMessage(data.message, true);
    } else {
      addChatMessage("I'm having trouble connecting. Please try again.", true);
    }
  } catch (error) {
    removeTypingIndicator();
    addChatMessage("Connection error. Please check your network.", true);
  } finally {
    chatbotSend.disabled = false;
    chatbotInput.focus();
  }
}

// Initialize chatbot with greeting
async function initChatbot() {
  try {
    const response = await fetch('/chat/greeting');
    if (response.ok) {
      const data = await response.json();
      addChatMessage(data.message, true);
    } else {
      addChatMessage("Hello! I'm your Detection Assistant. Upload a paper to analyze, then ask me about the results!", true);
    }
  } catch (error) {
    addChatMessage("Hello! I'm your Detection Assistant. Upload a paper to analyze, then ask me about the results!", true);
  }
}

// Update chatbot context when analysis completes
function updateChatbotContext(analysisData) {
  chatAnalysisContext = analysisData;
  
  // Show notification dot
  if (!chatbotContainer.classList.contains('open')) {
    chatNotification.style.display = 'block';
  }
  
  // Add automatic explanation if available
  if (analysisData.chatbot_explanation) {
    // If chat is open, add the message
    if (chatbotContainer.classList.contains('open')) {
      addChatMessage(analysisData.chatbot_explanation, true);
    }
  }
}

// Toggle chatbot visibility
chatbotToggle.addEventListener('click', () => {
  chatbotContainer.classList.toggle('open');
  chatNotification.style.display = 'none';
  
  // Initialize if first open
  if (chatbotContainer.classList.contains('open') && chatbotMessages.children.length === 0) {
    initChatbot();
  }
  
  // Focus input when opened
  if (chatbotContainer.classList.contains('open')) {
    chatbotInput.focus();
  }
});

// Close chatbot
chatbotClose.addEventListener('click', () => {
  chatbotContainer.classList.remove('open');
});

// Send message on button click
chatbotSend.addEventListener('click', () => {
  sendChatMessage(chatbotInput.value);
});

// Send message on Enter key
chatbotInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage(chatbotInput.value);
  }
});

// Handle suggestion chips
chatSuggestions.addEventListener('click', (e) => {
  if (e.target.classList.contains('suggestion-chip')) {
    const message = e.target.getAttribute('data-message');
    if (message) {
      sendChatMessage(message);
    }
  }
});

// Override the existing showResult to include GenAI features and update chatbot
const originalShowResult = showResult;
showResult = function(data) {
  originalShowResult(data);
  
  // Update chatbot context
  updateChatbotContext(data);
  
  // Add GenAI features display if available
  const genaiFeatures = data.scores?.genai_features || data.scores?.ai_score?.genai_features;
  if (genaiFeatures && genaiFeatures.features) {
    const existingGenai = document.getElementById('genaiSection');
    if (existingGenai) existingGenai.remove();
    
    const genaiSection = document.createElement('div');
    genaiSection.id = 'genaiSection';
    genaiSection.className = 'decision-box';
    genaiSection.style.marginTop = '20px';
    genaiSection.style.flexDirection = 'column';
    genaiSection.style.alignItems = 'stretch';
    genaiSection.style.background = 'rgba(139, 92, 246, 0.1)';
    genaiSection.style.border = '1px solid rgba(139, 92, 246, 0.3)';
    
    let genaiHtml = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <span style="font-size:12px;text-transform:uppercase;color:#a78bfa;letter-spacing:1px;">GenAI Pattern Analysis</span>
        <span style="font-size:16px;font-weight:700;color:white">${Math.round(genaiFeatures.composite_score * 100)}% AI Patterns</span>
      </div>
      <div style="width:100%;height:1px;background:rgba(139,92,246,0.2);margin-bottom:12px;"></div>
      <div class="genai-features-grid">
    `;
    
    const featureLabels = {
      'gpt_repetition': 'GPT Repetition',
      'gemini_overflow': 'Gemini Overflow',
      'claude_hedging': 'Claude Hedging',
      'burstiness': 'Low Burstiness',
      'citation_hallucination': 'Citation Issues',
      'perplexity': 'Low Perplexity'
    };
    
    for (const [key, feature] of Object.entries(genaiFeatures.features)) {
      const score = feature.score || 0;
      const level = score > 0.6 ? 'high' : score > 0.3 ? 'moderate' : 'low';
      const levelText = score > 0.6 ? 'High' : score > 0.3 ? 'Moderate' : 'Low';
      
      genaiHtml += `
        <div class="genai-feature-item">
          <div class="genai-feature-name">${featureLabels[key] || key}</div>
          <div class="genai-feature-score">${Math.round(score * 100)}%</div>
          <div class="genai-feature-level ${level}">${levelText}</div>
        </div>
      `;
    }
    
    genaiHtml += '</div>';
    
    // Add interpretation if available
    if (genaiFeatures.interpretation && genaiFeatures.interpretation.length > 0) {
      genaiHtml += `
        <div style="margin-top:16px;padding-top:12px;border-top:1px solid rgba(139,92,246,0.2);">
          <div style="font-size:11px;text-transform:uppercase;color:#a78bfa;letter-spacing:1px;margin-bottom:8px;">Key Findings</div>
          <ul style="margin:0;padding-left:16px;font-size:13px;color:#cbd5e1;">
            ${genaiFeatures.interpretation.map(i => `<li style="margin-bottom:4px;">${i}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    genaiSection.innerHTML = genaiHtml;
    result.appendChild(genaiSection);
  }
};

