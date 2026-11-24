/**
 * JobGuard360 - Real-Time Fake Job Detection Client
 * Connects Frontend Interface with Logistic Regression & SVM Inference Pipeline
 */

let sampleData = {};
let currentUploadedImageFile = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchSampleData();
});

// ==========================================================================
// 1. NAVIGATION & SECTION SWITCHING
// ==========================================================================
function switchSection(secId) {
  // Update sidebar active buttons
  const navBtns = document.querySelectorAll(".sidebar-nav .nav-item");
  navBtns.forEach(btn => {
    btn.classList.remove("active");
    if (btn.getAttribute("data-tab") === secId) {
      btn.classList.add("active");
    }
  });

  // Update mobile bottom bar buttons
  const bottomBtns = document.querySelectorAll(".mobile-bottom-bar .bottom-nav-item");
  bottomBtns.forEach(btn => {
    btn.classList.remove("active");
    if (btn.getAttribute("data-tab") === secId) {
      btn.classList.add("active");
    }
  });

  // Close mobile sidebar if open
  closeMobileSidebar();

  // Update visible sections
  const sections = document.querySelectorAll(".app-section");
  sections.forEach(sec => sec.classList.remove("active"));

  const target = document.getElementById(`sec-${secId}`);
  if (target) {
    target.classList.add("active");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// Mobile Sidebar Drawer Control
function toggleMobileSidebar() {
  const sidebar = document.getElementById("appSidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  if (!sidebar) return;
  const isOpen = sidebar.classList.toggle("mobile-open");
  if (backdrop) {
    backdrop.classList.toggle("active", isOpen);
  }
  document.body.classList.toggle("no-scroll", isOpen);
}

function closeMobileSidebar() {
  const sidebar = document.getElementById("appSidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  if (sidebar) sidebar.classList.remove("mobile-open");
  if (backdrop) backdrop.classList.remove("active");
  document.body.classList.remove("no-scroll");
}

// ==========================================================================
// 2. WORKBENCH TABS (Text Form, Photo Upload, URL Link, Raw Text)
// ==========================================================================
function setWorkbenchTab(tabType) {
  const tabBtns = document.querySelectorAll(".wb-tab");
  tabBtns.forEach(b => b.classList.remove("active"));

  const panes = document.querySelectorAll(".wb-pane");
  panes.forEach(p => p.classList.remove("active"));

  if (tabType === "text") {
    document.getElementById("tabBtnText")?.classList.add("active");
    document.getElementById("paneText")?.classList.add("active");
  } else if (tabType === "photo") {
    document.getElementById("tabBtnPhoto")?.classList.add("active");
    document.getElementById("panePhoto")?.classList.add("active");
  } else if (tabType === "link") {
    document.getElementById("tabBtnLink")?.classList.add("active");
    document.getElementById("paneLink")?.classList.add("active");
  } else if (tabType === "raw") {
    document.getElementById("tabBtnRaw")?.classList.add("active");
    document.getElementById("paneRaw")?.classList.add("active");
  }
}

function updateEngineChoice(choice) {
  const lbl = document.getElementById("currentEngineLabel");
  if (!lbl) return;
  if (choice === "logistic_regression") {
    lbl.innerText = "Logistic Regression";
  } else if (choice === "svm") {
    lbl.innerText = "Support Vector Machine";
  } else {
    lbl.innerText = "Dual Consensus (LR + SVM)";
  }
}

// ==========================================================================
// 3. SAMPLE PRELOADING & INSTANT EXECUTION
// ==========================================================================
async function fetchSampleData() {
  try {
    const res = await fetch("/api/samples");
    const json = await res.json();
    if (json.status === "success") {
      sampleData = json.data;
    }
  } catch (err) {
    console.error("Failed to load sample dataset:", err);
  }
}

function applySampleJob(sampleKey) {
  // Ensure we are in detector section and text form tab
  switchSection("detector");
  setWorkbenchTab("text");

  if (!sampleData || !sampleData.legitimate) return;

  let s = null;
  if (sampleKey === "legit_tech") s = sampleData.legitimate[0];
  if (sampleKey === "legit_health") s = sampleData.legitimate[1];
  if (sampleKey === "scam_data") s = sampleData.fraudulent[0];
  if (sampleKey === "scam_shopper") s = sampleData.fraudulent[1];
  if (sampleKey === "scam_crypto") s = sampleData.fraudulent[2];

  if (s) {
    document.getElementById("inpTitle").value = s.title || "";
    document.getElementById("inpCompany").value = s.company_profile || "";
    document.getElementById("inpDescription").value = s.description || "";
    document.getElementById("inpRequirements").value = s.requirements || "";
    document.getElementById("inpBenefits").value = s.benefits || "";
    document.getElementById("chkLogo").checked = Boolean(s.has_company_logo);
    document.getElementById("chkQuestions").checked = Boolean(s.has_questions);
    document.getElementById("chkTelecommute").checked = Boolean(s.telecommuting);

    // Auto trigger instant detection so the user sees results immediately
    triggerDetectionCall({
      title: s.title || "",
      company_profile: s.company_profile || "",
      description: s.description || "",
      requirements: s.requirements || "",
      benefits: s.benefits || "",
      has_company_logo: s.has_company_logo ? 1 : 0,
      has_questions: s.has_questions ? 1 : 0,
      telecommuting: s.telecommuting ? 1 : 0,
      model_choice: document.getElementById("engineSelect").value
    });
  }
}

function clearJobWorkbench() {
  document.getElementById("inpTitle").value = "";
  document.getElementById("inpCompany").value = "";
  document.getElementById("inpDescription").value = "";
  document.getElementById("inpRequirements").value = "";
  document.getElementById("inpBenefits").value = "";
  document.getElementById("chkLogo").checked = true;
  document.getElementById("chkQuestions").checked = true;
  document.getElementById("chkTelecommute").checked = false;

  document.getElementById("resEmptyState").style.display = "flex";
  document.getElementById("resActiveState").style.display = "none";
}

// ==========================================================================
// 4. DETECTION EXECUTION & RESULTS RENDERING
// ==========================================================================
function handleStructuredFormSubmit(e) {
  e.preventDefault();
  const payload = {
    title: document.getElementById("inpTitle").value.trim(),
    company_profile: document.getElementById("inpCompany").value.trim(),
    description: document.getElementById("inpDescription").value.trim(),
    requirements: document.getElementById("inpRequirements").value.trim(),
    benefits: document.getElementById("inpBenefits").value.trim(),
    has_company_logo: document.getElementById("chkLogo").checked ? 1 : 0,
    has_questions: document.getElementById("chkQuestions").checked ? 1 : 0,
    telecommuting: document.getElementById("chkTelecommute").checked ? 1 : 0,
    model_choice: document.getElementById("engineSelect").value
  };
  triggerDetectionCall(payload);
}

async function triggerDetectionCall(payload) {
  const btn = document.getElementById("btnRunMain");
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span>Evaluating with LR & SVM...</span>`;

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === "success") {
      renderActiveResults(json.data);
    } else {
      alert("Detection error: " + (json.message || "Failed to analyze."));
    }
  } catch (err) {
    console.error("Prediction request failed:", err);
    alert("Connection error while analyzing posting.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
}

function renderActiveResults(data) {
  document.getElementById("resEmptyState").style.display = "none";
  const activeDiv = document.getElementById("resActiveState");
  activeDiv.style.display = "block";

  const isFake = data.is_fraudulent;
  const score = data.risk_score;
  const badgeClass = data.badge_class;

  // 1. Verdict Banner
  const banner = document.getElementById("bannerVerdict");
  banner.className = `verdict-banner-box ${badgeClass}`;
  document.getElementById("vTagLabel").innerText = isFake ? "CRITICAL ALERT" : "VERIFIED AUTHENTIC";
  document.getElementById("vHeadline").innerText = data.verdict;
  document.getElementById("vSubline").innerText = isFake
    ? "High probability of recruitment fraud, off-platform communication, or financial check requests."
    : "Verified organizational background, standard duties, and formal hiring criteria.";

  // 2. Risk Radial Gauge
  document.getElementById("valRiskPercent").innerText = `${score}%`;
  const pill = document.getElementById("pillRiskLevel");
  pill.className = `risk-badge-pill ${badgeClass}`;
  pill.innerText = data.risk_level;

  const desc = document.getElementById("txtRiskSummary");
  if (isFake) {
    desc.innerText = "WARNING: Posting matches known scam signatures (e.g. advance equipment checks, untraceable Telegram/WhatsApp interviews, or money mule processing). Do NOT submit personal credentials or banking information.";
  } else {
    desc.innerText = "SAFE: Posting exhibits established corporate attributes, verifiable responsibilities, and official application questionnaire criteria.";
  }

  document.getElementById("lblActiveEngine").innerText = data.primary_model;

  // Animate SVG Radial Gauge
  const circumference = 2 * Math.PI * 68;
  const offset = circumference - (score / 100) * circumference;
  const circle = document.getElementById("radialCircleFill");
  circle.style.strokeDashoffset = offset;
  circle.style.stroke = score > 50 ? "var(--accent-red)" : (score > 25 ? "var(--accent-orange)" : "var(--accent-green)");

  // 3. Dual Model Breakdown
  const lr = data.model_breakdown.logistic_regression;
  const svm = data.model_breakdown.svm;

  document.getElementById("valLrScore").innerText = `${lr.probability}%`;
  const barLr = document.getElementById("barLrProgress");
  barLr.style.width = `${lr.probability}%`;
  barLr.className = lr.is_fraudulent ? "m-progress-fill danger" : "m-progress-fill";
  document.getElementById("lblLrVerdict").innerText = lr.is_fraudulent ? "Fraudulent" : "Legitimate";
  document.getElementById("lblLrVerdict").style.color = lr.is_fraudulent ? "var(--accent-red)" : "var(--accent-green)";

  document.getElementById("valSvmScore").innerText = `${svm.probability}%`;
  const barSvm = document.getElementById("barSvmProgress");
  barSvm.style.width = `${svm.probability}%`;
  barSvm.className = svm.is_fraudulent ? "m-progress-fill danger" : "m-progress-fill";
  document.getElementById("lblSvmVerdict").innerText = svm.is_fraudulent ? "Fraudulent" : "Legitimate";
  document.getElementById("lblSvmVerdict").style.color = svm.is_fraudulent ? "var(--accent-red)" : "var(--accent-green)";

  // 4. Detected Keywords
  const kwWrap = document.getElementById("wrapKeywordTags");
  if (data.detected_keywords && data.detected_keywords.length > 0) {
    kwWrap.innerHTML = data.detected_keywords.map(kw => `<span class="kw-pill">${kw}</span>`).join('');
  } else {
    kwWrap.innerHTML = `<span class="no-tags-note">No high-risk scam triggers detected.</span>`;
  }

  // 5. Red Flags
  const flagsWrap = document.getElementById("wrapRedFlags");
  if (data.red_flags && data.red_flags.length > 0) {
    flagsWrap.innerHTML = data.red_flags.map(f => `
      <div class="flag-alert-item">
        <strong class="sev-${f.severity}">[${f.severity}]</strong>
        <span><strong>${f.title}:</strong> ${f.description}</span>
      </div>
    `).join('');
  } else {
    flagsWrap.innerHTML = `<p class="no-tags-note">No security violations recorded.</p>`;
  }

  // 6. Trust Signals
  const trustWrap = document.getElementById("wrapTrustSignals");
  if (data.trust_signals && data.trust_signals.length > 0) {
    trustWrap.innerHTML = data.trust_signals.map(s => `<li>${s}</li>`).join('');
  } else {
    trustWrap.innerHTML = `<li style="color: var(--text-dim);">No verified corporate trust signals recorded.</li>`;
  }

  // Smoothly scroll down on mobile/tablet viewports so results are immediately visible
  if (window.innerWidth <= 1024) {
    const resCard = document.getElementById("resultsContainer");
    if (resCard) {
      setTimeout(() => {
        resCard.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 120);
    }
  }
}

// ==========================================================================
// 5. PHOTO / SCREENSHOT SCANNING
// ==========================================================================
function handleImageSelection(input) {
  const file = input.files[0];
  if (!file) return;

  currentUploadedImageFile = file;
  const reader = new FileReader();
  reader.onload = function(e) {
    document.getElementById("imgThumb").src = e.target.result;
    document.getElementById("imgFileName").innerText = file.name;
    document.getElementById("imgPreviewCard").style.display = "flex";
  };
  reader.readAsDataURL(file);
}

async function executeImageScan() {
  if (!currentUploadedImageFile) {
    alert("Please select an image file first.");
    return;
  }

  const btn = document.getElementById("btnScanImage");
  const orig = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = "<span>Analyzing Image with ML...</span>";

  const formData = new FormData();
  formData.append("file", currentUploadedImageFile);
  formData.append("model_choice", document.getElementById("engineSelect").value);

  try {
    const res = await fetch("/api/scan-image", { method: "POST", body: formData });
    const json = await res.json();
    if (json.status === "success") {
      renderActiveResults(json.data);
    } else {
      alert("Image analysis error: " + json.message);
    }
  } catch (err) {
    console.error(err);
    alert("Failed to analyze image.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = orig;
  }
}

// ==========================================================================
// 6. URL / LINK SCANNING
// ==========================================================================
async function executeUrlScan() {
  const url = document.getElementById("inpJobUrl").value.trim();
  if (!url) {
    alert("Please enter a valid job link or URL.");
    return;
  }

  try {
    const res = await fetch("/api/scan-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
        model_choice: document.getElementById("engineSelect").value
      })
    });
    const json = await res.json();
    if (json.status === "success") {
      renderActiveResults(json.data);
    } else {
      alert("URL scan error: " + json.message);
    }
  } catch (err) {
    console.error(err);
    alert("Failed to scan URL.");
  }
}

// ==========================================================================
// 7. RAW TEXT SCANNING
// ==========================================================================
function executeRawTextScan() {
  const raw = document.getElementById("inpRawText").value.trim();
  if (!raw) {
    alert("Please paste job text to scan.");
    return;
  }

  triggerDetectionCall({
    title: raw.slice(0, 60),
    company_profile: "",
    description: raw,
    requirements: "",
    benefits: "",
    has_company_logo: 0,
    has_questions: 0,
    telecommuting: 1,
    model_choice: document.getElementById("engineSelect").value
  });
}

// ==========================================================================
// 8. BATCH SCANNER (CSV & 10 SAMPLES)
// ==========================================================================
function executeSampleBatchScan() {
  if (!sampleData || !sampleData.legitimate) return;

  const mockBatch = [
    ...sampleData.legitimate,
    ...sampleData.fraudulent,
    {
      title: "Senior Cloud Infrastructure Architect",
      company_profile: "Apex Enterprise Systems designs global multicloud platforms.",
      description: "Design Kubernetes orchestration and microservice scalability across AWS.",
      requirements: "8+ years enterprise cloud architecture.",
      benefits: "Health, 401(k), equity, generous PTO.",
      has_company_logo: 1,
      has_questions: 1,
      telecommuting: 1
    },
    {
      title: "Immediate Check Clearing Assistant ($55/hr)",
      company_profile: "",
      description: "Receive company checks into your personal checking account. Keep $500 fee, wire balance via Western Union.",
      requirements: "Must have active checking account.",
      benefits: "Weekly payouts.",
      has_company_logo: 0,
      has_questions: 0,
      telecommuting: 1
    }
  ];

  fetch("/api/batch-predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jobs: mockBatch, model_choice: "both" })
  })
    .then(r => r.json())
    .then(json => {
      if (json.status === "success") {
        renderBatchTable(json.data);
      }
    })
    .catch(err => console.error("Batch error:", err));
}

function handleBatchFileUpload(input) {
  const file = input.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("model_choice", "both");

  fetch("/api/upload-csv", { method: "POST", body: formData })
    .then(r => r.json())
    .then(json => {
      if (json.status === "success") {
        renderBatchTable(json.data);
      } else {
        alert("Upload error: " + json.message);
      }
    })
    .catch(err => console.error("CSV error:", err));
}

function renderBatchTable(data) {
  document.getElementById("batchStatsStrip").style.display = "grid";
  document.getElementById("batchTableContainer").style.display = "block";

  document.getElementById("statBatchTotal").innerText = data.total_analyzed;
  document.getElementById("statBatchFake").innerText = data.flagged_fraudulent;
  document.getElementById("statBatchLegit").innerText = data.verified_legitimate;
  document.getElementById("statBatchRate").innerText = `${data.fraud_rate_percent}%`;

  const tbody = document.getElementById("tbodyBatchRows");
  tbody.innerHTML = data.results.map(row => {
    const isFake = row.is_fraudulent;
    const badge = isFake
      ? `<span class="act-pill red">SCAM</span>`
      : `<span class="act-pill green">LEGIT</span>`;

    return `
      <tr>
        <td>${badge}</td>
        <td><strong>${escapeHtml(row.title)}</strong></td>
        <td><strong style="color: ${isFake ? '#e11d48' : '#059669'};">${row.risk_score}%</strong></td>
        <td>${row.lr_prob}%</td>
        <td>${row.svm_prob}%</td>
        <td>${row.flag_count} threat alert(s)</td>
      </tr>
    `;
  }).join('');
}

function escapeHtml(t) {
  if (!t) return "";
  return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function openApiDocs() {
  window.open("/docs", "_blank");
}

function retrainModelsInfo() {
  switchSection("models");
}

function filterSampleKeywords(query) {
  if (!query) return;
  const q = query.toLowerCase();
  if (q.includes("scam") || q.includes("fake") || q.includes("telegram") || q.includes("check")) {
    applySampleJob("scam_data");
  } else if (q.includes("real") || q.includes("tech") || q.includes("software") || q.includes("engineer")) {
    applySampleJob("legit_tech");
  }
}

// ==========================================================================
// 9. INSTANT SAMPLE IMAGE & URL LOADERS
// ==========================================================================
const SAMPLE_IMAGE_MAP = {
  fake_telegram: {
    path: "/sample_images/fake_job_telegram_data_entry.png",
    name: "fake_job_telegram_data_entry.png"
  },
  fake_mystery: {
    path: "/sample_images/fake_job_check_mystery_shopper.png",
    name: "fake_job_check_mystery_shopper.png"
  },
  valid_engineer: {
    path: "/sample_images/valid_job_software_engineer.png",
    name: "valid_job_software_engineer.png"
  },
  valid_clinical: {
    path: "/sample_images/valid_job_clinical_coordinator.png",
    name: "valid_job_clinical_coordinator.png"
  }
};

async function loadSampleImage(key) {
  const item = SAMPLE_IMAGE_MAP[key];
  if (!item) return;

  setWorkbenchTab("photo");
  document.getElementById("imgThumb").src = item.path;
  document.getElementById("imgFileName").innerText = item.name;
  document.getElementById("imgFileSize").innerText = "Pre-generated test scenario ready for ML scan";
  document.getElementById("imgPreviewCard").style.display = "flex";

  try {
    // Fetch blob and convert to File object
    const res = await fetch(item.path);
    const blob = await res.blob();
    currentUploadedImageFile = new File([blob], item.name, { type: "image/png" });
    
    // Automatically execute the scan so results are instant!
    executeImageScan();
  } catch (err) {
    console.error("Failed to load sample image blob:", err);
  }
}

function loadSampleUrl(url) {
  setWorkbenchTab("link");
  const input = document.getElementById("inpJobUrl");
  if (input) {
    input.value = url;
    executeUrlScan();
  }
}
