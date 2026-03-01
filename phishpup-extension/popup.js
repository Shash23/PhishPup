var statusBadge = document.getElementById('statusBadge');
var summaryText = document.getElementById('summaryText');
var explanationText = document.getElementById('explanationText');
var draftBox = document.getElementById('draftBox');
var conversationBox = document.getElementById('conversationBox');
var detailsRaw = document.getElementById('detailsRaw');
var detailsSection = document.getElementById('detailsSection');
var toggleDetailsBtn = document.getElementById('toggleDetails');

function setBadge(text, riskClass) {
  statusBadge.textContent = text || '';
  statusBadge.className = 'status-badge ' + (riskClass || 'risk-none');
}

function clearResult() {
  setBadge('', 'risk-none');
  summaryText.textContent = '';
  explanationText.textContent = '';
  draftBox.textContent = '';
  conversationBox.textContent = '';
  detailsRaw.textContent = '';
}

toggleDetailsBtn.addEventListener('click', function () {
  var visible = detailsSection.classList.toggle('is-visible');
  toggleDetailsBtn.textContent = visible ? 'Hide Details' : 'Show Details';
});

document.getElementById('check').addEventListener('click', async function () {
  clearResult();

  try {
    var tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs.length || !tabs[0].id) {
      setBadge('No tab. Open Gmail and try again.');
      return;
    }

    var results = await chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      files: ['extract.js']
    });

    var raw = results && results[0] && results[0].result != null ? results[0].result : null;
    var result = raw && typeof raw.then === 'function' ? await raw : raw;

    if (!result || typeof result.draft !== 'string' || !result.draft.trim()) {
      setBadge('No email detected');
      return;
    }

    draftBox.textContent = result.draft || '(empty)';
    conversationBox.textContent = result.conversation || '(no conversation found)';

    var res = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        draft: result.draft,
        conversation: result.conversation || '',
        metadata: {
          source: 'gmail-extension',
          recipients: result.recipients || []
        }
      })
    });

    if (!res.ok) {
      setBadge('Backend not reachable. Start server.');
      return;
    }

    var analysis = await res.json();
    var riskLevel = (analysis.risk_level || '').toUpperCase();
    var label = riskLevel === 'LOW' ? 'SAFE' : riskLevel === 'MEDIUM' ? 'CHECK' : riskLevel === 'HIGH' ? 'STOP_VERIFY' : riskLevel;
    var riskClass = riskLevel === 'LOW' ? 'risk-safe' : riskLevel === 'MEDIUM' ? 'risk-check' : riskLevel === 'HIGH' ? 'risk-stop' : 'risk-none';

    setBadge(label, riskClass);
    summaryText.textContent = 'Action: ' + (analysis.action || '');
    explanationText.textContent = analysis.explanation || '';

    var pressureStr = Array.isArray(analysis.pressure_signals) && analysis.pressure_signals.length
      ? analysis.pressure_signals.join(', ')
      : 'none';
    detailsRaw.textContent = 'Action: ' + (analysis.action || '') + '\nPressure: ' + pressureStr + '\n\n' + (analysis.explanation || '');
  } catch (err) {
    setBadge('Backend not reachable. Start server.');
  }
});
