// Dashboard-specific behaviour: chart rendering and scan controls.
// Uses data attributes rendered by the template and the /status and /scan API endpoints.

(function () {
  function getChartElements() {
    var canvas = document.getElementById('progress-chart');
    var emptyEl = document.getElementById('chart-empty');
    var raw = canvas ? canvas.getAttribute('data-chart') || '[]' : '[]';
    var data;
    try {
      data = JSON.parse(raw);
      if (!Array.isArray(data)) data = [];
    } catch (e) {
      data = [];
    }
    return { canvas: canvas, emptyEl: emptyEl, chartData: data };
  }

  function initChart() {
    var parts = getChartElements();
    var canvas = parts.canvas;
    var emptyEl = parts.emptyEl;
    var chartData = parts.chartData;

    if (typeof Chart !== 'undefined') {
      Chart.defaults.color = '#8b949e';
      Chart.defaults.borderColor = '#2d3a4d';
      Chart.defaults.font.family = 'system-ui, -apple-system, sans-serif';
    }

    if (!canvas) {
      if (emptyEl) emptyEl.style.display = 'block';
      return;
    }

    if (chartData.length > 0 && typeof Chart !== 'undefined') {
      if (emptyEl) emptyEl.style.display = 'none';
      var labels = chartData.map(function (d) { return d.label; });
      var findings = chartData.map(function (d) { return d.total_findings; });
      var scores = chartData.map(function (d) { return d.score; });
      new Chart(canvas, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Total findings',
              data: findings,
              borderColor: 'rgb(88, 166, 255)',
              backgroundColor: 'rgba(88, 166, 255, 0.1)',
              fill: true,
              yAxisID: 'y'
            },
            {
              label: 'Risk score (0–100)',
              data: scores,
              borderColor: 'rgb(243, 133, 81)',
              backgroundColor: 'rgba(243, 133, 81, 0.1)',
              fill: true,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          aspectRatio: 2,
          interaction: { mode: 'index', intersect: false },
          plugins: { legend: { position: 'top' } },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: { display: true, text: 'Total findings' },
              min: 0,
              ticks: { precision: 0 }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: { display: true, text: 'Risk score' },
              min: 0,
              max: 100,
              grid: { drawOnChartArea: false }
            }
          }
        }
      });
    } else {
      if (emptyEl) emptyEl.style.display = 'block';
      canvas.style.display = 'none';
    }
  }

  function initScanControls() {
    var btn = document.getElementById('btn-start-scan');
    var feedback = document.getElementById('scan-feedback');
    var feedbackGuide = document.getElementById('scan-feedback-guide');
    var statusRunning = document.getElementById('status-running');
    var statusSession = document.getElementById('status-session');
    var statusFindings = document.getElementById('status-findings');

    function pollStatus() {
      fetch('/status')
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (statusRunning) statusRunning.textContent = d.running ? 'Running' : 'Idle';
          if (statusSession) statusSession.textContent = d.current_session_id || '—';
          if (statusFindings) statusFindings.textContent = d.findings_count;
          if (d.running) {
            if (btn) btn.disabled = true;
            setTimeout(pollStatus, 2000);
          } else {
            if (btn) btn.disabled = false;
            if (document.getElementById('stat-db')) {
              location.reload();
            }
          }
        })
        .catch(function () {
          // Silent failure; do not spam the UI.
        });
    }

    if (btn) {
      btn.addEventListener('click', function () {
        var tenantInput = document.getElementById('scan-tenant');
        var tenant = (tenantInput && tenantInput.value && tenantInput.value.trim())
          ? tenantInput.value.trim()
          : null;
        var techInput = document.getElementById('scan-technician');
        var technician = (techInput && techInput.value && techInput.value.trim())
          ? techInput.value.trim()
          : null;
        var scanCompressedEl = document.getElementById('scan-compressed');
        var scanCompressed = scanCompressedEl && scanCompressedEl.checked;
        var contentTypeEl = document.getElementById('scan-content-type');
        var contentTypeCheck = contentTypeEl && contentTypeEl.checked;

        if (feedback) feedback.textContent = 'Starting…';
        if (feedbackGuide) { feedbackGuide.textContent = ''; feedbackGuide.style.display = 'none'; }
        if (btn) btn.disabled = true;
        var body = {};
        if (tenant != null) body.tenant = tenant;
        if (technician != null) body.technician = technician;
        if (scanCompressed) body.scan_compressed = true;
        if (contentTypeCheck) body.content_type_check = true;

        var opts = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        };

        fetch('/scan', opts)
          .then(function (r) {
            if (!r.ok) {
              var err = new Error('Request failed: ' + r.status + ' ' + (r.statusText || ''));
              err.status = r.status;
              err.response = r;
              throw err;
            }
            return r.json();
          })
          .then(function (d) {
            if (feedback) {
              var sid = (d.session_id || '').slice(0, 16);
              feedback.textContent = 'Started: ' + (sid ? sid + '…' : '');
            }
            if (feedbackGuide) { feedbackGuide.textContent = ''; feedbackGuide.style.display = 'none'; }
            pollStatus();
          })
          .catch(function (e) {
            if (btn) btn.disabled = false;
            var msg = e.message || String(e);
            var guide = '';
            if (e.status === 409) {
              msg = 'Scan already in progress.';
              guide = 'Wait for the current scan to finish, or restart the API if it is stuck.';
            } else if (e.status === 429) {
              msg = 'Rate limited; try again shortly.';
              guide = 'Wait and try again, or adjust rate_limit.max_concurrent_scans and min_interval_seconds in config.';
            } else if (e.status === 401 || e.status === 403) {
              msg = 'Not authorized (' + e.status + ').';
              guide = 'Check API key or auth configuration if the API is protected.';
            } else if (!e.status && !e.response) {
              guide = 'Request did not reach the server. Check network, CORS, or ad-blockers; ensure the API is running.';
            } else if (e.status >= 500) {
              guide = 'Server error. Check API logs and try again.';
            }
            function showError(displayMsg, displayGuide) {
              if (feedback) feedback.textContent = 'Error: ' + (displayMsg || msg);
              if (feedbackGuide) {
                feedbackGuide.textContent = displayGuide || guide ? 'What to do: ' + (displayGuide || guide) : '';
                feedbackGuide.style.display = (displayGuide || guide) ? 'block' : 'none';
              }
            }
            if (e.response) {
              e.response.text().then(function (t) {
                var displayMsg = msg;
                var displayGuide = guide;
                try {
                  var j = JSON.parse(t);
                  if (j.detail) {
                    if (typeof j.detail === 'string') displayMsg = j.detail;
                    else if (j.detail.reason) { displayMsg = j.detail.reason; if (j.detail.retry_after_seconds != null) displayGuide = 'Retry after ' + j.detail.retry_after_seconds + ' seconds, or adjust rate_limit in config.'; }
                    else displayMsg = JSON.stringify(j.detail);
                  }
                } catch (_) {}
                showError(displayMsg, displayGuide);
              }).catch(function () { showError(msg, guide); });
            } else {
              showError(msg, guide);
            }
          });
      });
    }

    if (statusRunning && statusRunning.textContent === 'Running') {
      pollStatus();
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    try {
      initChart();
    } catch (e) {
      // Chart.js may fail to load (CDN/blocker); ensure scan controls still work
    }
    initScanControls();
  });
})();

