/**
 * Custom Bytecode VM Frontend Visualizer Controller
 */

// Application State
let currentEnvironment = {};
let currentTrace = [];
let currentBytecode = [];
let currentStepIndex = 0;
let isPlaying = false;
let playInterval = null;

// DOM Elements
const inputExpr = document.getElementById("expression-input");
const btnEvaluate = document.getElementById("btn-evaluate");
const btnClearEnv = document.getElementById("btn-clear-env");
const errorCard = document.getElementById("error-card");
const errorType = document.getElementById("error-type");
const errorCoords = document.getElementById("error-coords");
const errorMsg = document.getElementById("error-message");
const errorDiagnostic = document.getElementById("error-diagnostic");

// Metrics
const metricResult = document.getElementById("metric-result");
const metricTime = document.getElementById("metric-time");
const metricInstructions = document.getElementById("metric-instructions");
const metricStack = document.getElementById("metric-stack");

// Environment & Tabs
const envContainer = document.getElementById("env-container");
const envCount = document.getElementById("env-count");
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanes = document.querySelectorAll(".tab-pane");

// Animator Controls
const btnStepFirst = document.getElementById("btn-step-first");
const btnStepPrev = document.getElementById("btn-step-prev");
const btnStepPlay = document.getElementById("btn-step-play");
const btnStepNext = document.getElementById("btn-step-next");
const btnStepLast = document.getElementById("btn-step-last");
const traceSlider = document.getElementById("trace-slider");
const stepCounter = document.getElementById("step-counter");

const stepBadge = document.getElementById("step-badge");
const stepOpcode = document.getElementById("step-opcode");
const stepArg = document.getElementById("step-arg");
const stepAction = document.getElementById("step-action");
const stackStage = document.getElementById("stack-stage");
const stackDepthLabel = document.getElementById("stack-depth-label");

// Tables & Trees
const tbodyBytecode = document.getElementById("tbody-bytecode");
const tbodyTokens = document.getElementById("tbody-tokens");
const astTreeContainer = document.getElementById("ast-tree-container");
const rpnChipsContainer = document.getElementById("rpn-chips-container");

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupPresets();
  setupControls();

  // Initial evaluation
  evaluateCurrentExpression();
});

// Setup Tab Switching
function setupTabs() {
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

// Preset Chip Buttons
function setupPresets() {
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const expr = chip.getAttribute("data-expr");
      inputExpr.value = expr;
      evaluateCurrentExpression();
    });
  });
}

// Event Listeners for Controls
function setupControls() {
  btnEvaluate.addEventListener("click", () => evaluateCurrentExpression());

  inputExpr.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      evaluateCurrentExpression();
    }
  });

  btnClearEnv.addEventListener("click", () => {
    currentEnvironment = {};
    renderEnvironment();
    evaluateCurrentExpression();
  });

  // Playback Buttons
  btnStepFirst.addEventListener("click", () => goToStep(0));
  btnStepPrev.addEventListener("click", () => goToStep(currentStepIndex - 1));
  btnStepNext.addEventListener("click", () => goToStep(currentStepIndex + 1));
  btnStepLast.addEventListener("click", () => goToStep(currentTrace.length - 1));

  btnStepPlay.addEventListener("click", togglePlay);

  traceSlider.addEventListener("input", (e) => {
    goToStep(parseInt(e.target.value, 10));
  });
}

// Core Evaluation API Call
async function evaluateCurrentExpression() {
  const expr = inputExpr.value.trim();
  if (!expr) return;

  hideError();

  try {
    const response = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        expression: expr,
        environment: currentEnvironment,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      showError(data);
      return;
    }

    // Update Persistent Environment
    if (data.environment) {
      currentEnvironment = data.environment;
      renderEnvironment();
    }

    // Update Metrics
    metricResult.textContent = data.result;
    metricTime.textContent = `${data.metrics.execution_time_us} µs`;
    metricInstructions.textContent = `${data.metrics.instruction_count} ops`;
    metricStack.textContent = `${data.metrics.peak_stack_depth} items`;

    // Save Data
    currentTrace = data.trace || [];
    currentBytecode = data.bytecode || [];

    // Populate Inspector Tabs
    renderBytecodeTable(data.bytecode);
    renderTokensTable(data.tokens);
    renderAstTree(data.ast);
    renderRpnChips(data.rpn);

    // Setup Animator
    initAnimator();

    updateServerStatus(true);
  } catch (err) {
    updateServerStatus(false);
    showError({
      error_type: "NetworkError",
      message: "Cannot connect to FastAPI backend server (http://127.0.0.1:8000). Please ensure the backend server is running via: python -m uvicorn api.main:app --port 8000",
      diagnostic: err.message,
    });
  }
}

// Live Server Connectivity Status Indicator
function updateServerStatus(isOnline) {
  const badge = document.getElementById("vm-status-badge");
  if (!badge) return;
  if (isOnline) {
    badge.className = "badge badge-glow";
    badge.innerHTML = `<span class="status-dot"></span> VM Online`;
  } else {
    badge.className = "badge";
    badge.style.borderColor = "var(--accent-rose)";
    badge.style.color = "var(--accent-rose)";
    badge.innerHTML = `<span class="status-dot" style="background:var(--accent-rose);box-shadow:0 0 8px var(--accent-rose)"></span> VM Offline`;
  }
}

// Render Active Variables Store
function renderEnvironment() {
  const keys = Object.keys(currentEnvironment);
  envCount.textContent = `${keys.length} vars`;

  if (keys.length === 0) {
    envContainer.innerHTML = `<p class="empty-state">No variables currently defined.</p>`;
    return;
  }

  const list = document.createElement("div");
  list.className = "env-tag-list";
  keys.sort().forEach((key) => {
    const tag = document.createElement("div");
    tag.className = "env-tag";
    tag.innerHTML = `<span class="var-name">${key}</span>: <span>${currentEnvironment[key]}</span>`;
    list.appendChild(tag);
  });

  envContainer.innerHTML = "";
  envContainer.appendChild(list);
}

// Initialize Stack Animator
function initAnimator() {
  stopPlay();
  traceSlider.min = 0;
  traceSlider.max = Math.max(0, currentTrace.length - 1);
  goToStep(0);
}

// Navigate to a Specific Trace Step
function goToStep(index) {
  if (currentTrace.length === 0) {
    stepCounter.textContent = "Step 0 / 0";
    stackDepthLabel.textContent = "Depth: 0";
    stackStage.innerHTML = `<div class="stack-bottom-line">STACK BOTTOM</div>`;
    return;
  }

  currentStepIndex = Math.max(0, Math.min(index, currentTrace.length - 1));
  traceSlider.value = currentStepIndex;
  stepCounter.textContent = `Step ${currentStepIndex + 1} / ${currentTrace.length}`;

  const step = currentTrace[currentStepIndex];

  // Update Step Card
  stepBadge.textContent = `IP: ${step.ip}`;
  stepOpcode.textContent = step.instruction.opcode;
  stepArg.textContent = step.instruction.arg !== null ? `${step.instruction.arg}` : "";
  stepAction.textContent = step.action || step.instruction.description;

  // Highlight Disassembly Row
  highlightBytecodeRow(step.ip);

  // Render Visual Stack
  renderStackVisual(step.stack_after);
}

// Render Stack Frames Dynamically
function renderStackVisual(stackItems) {
  stackDepthLabel.textContent = `Depth: ${stackItems.length}`;
  stackStage.innerHTML = `<div class="stack-bottom-line">STACK BOTTOM</div>`;

  if (!stackItems || stackItems.length === 0) {
    const emptyNotice = document.createElement("div");
    emptyNotice.className = "empty-state";
    emptyNotice.textContent = "(Stack is currently empty)";
    stackStage.appendChild(emptyNotice);
    return;
  }

  stackItems.forEach((val, idx) => {
    const frame = document.createElement("div");
    frame.className = "stack-frame";
    if (idx === stackItems.length - 1) {
      frame.classList.add("top-frame");
    }

    const isTop = idx === stackItems.length - 1;
    frame.innerHTML = `
      <span class="frame-index">[${idx}]</span>
      <span class="frame-val">${val}</span>
      ${isTop ? `<span class="frame-top-tag">TOP</span>` : `<span></span>`}
    `;
    stackStage.appendChild(frame);
  });
}

// Highlight Bytecode Row
function highlightBytecodeRow(ip) {
  const rows = tbodyBytecode.querySelectorAll("tr");
  rows.forEach((row, idx) => {
    if (idx === ip) {
      row.classList.add("row-active");
    } else {
      row.classList.remove("row-active");
    }
  });
}

// Play / Pause Animation Loop
function togglePlay() {
  if (isPlaying) {
    stopPlay();
  } else {
    startPlay();
  }
}

function startPlay() {
  if (currentTrace.length === 0) return;
  isPlaying = true;
  btnStepPlay.textContent = "⏸ Pause";

  if (currentStepIndex >= currentTrace.length - 1) {
    currentStepIndex = 0;
  }

  playInterval = setInterval(() => {
    if (currentStepIndex < currentTrace.length - 1) {
      goToStep(currentStepIndex + 1);
    } else {
      stopPlay();
    }
  }, 600);
}

function stopPlay() {
  isPlaying = false;
  btnStepPlay.textContent = "▶ Play";
  if (playInterval) {
    clearInterval(playInterval);
    playInterval = null;
  }
}

// Render Bytecode Table
function renderBytecodeTable(bytecode) {
  tbodyBytecode.innerHTML = "";
  if (!bytecode || bytecode.length === 0) {
    tbodyBytecode.innerHTML = `<tr><td colspan="4" class="empty-state">No bytecode compiled.</td></tr>`;
    return;
  }

  bytecode.forEach((instr) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${String(instr.offset).padStart(4, "0")}</td>
      <td><strong>${instr.opcode}</strong></td>
      <td>${instr.arg !== null ? `<span style="color:var(--accent-amber)">${instr.arg}</span>` : ""}</td>
      <td style="color:var(--text-muted)">${instr.description || ""}</td>
    `;
    tbodyBytecode.appendChild(row);
  });
}

// Render Lexer Tokens Table
function renderTokensTable(tokens) {
  tbodyTokens.innerHTML = "";
  if (!tokens || tokens.length === 0) {
    tbodyTokens.innerHTML = `<tr><td colspan="5" class="empty-state">No tokens available.</td></tr>`;
    return;
  }

  tokens.forEach((t, idx) => {
    const row = document.createElement("tr");
    let tagClass = "token-OP";
    if (t.type === "NUMBER") tagClass = "token-NUMBER";
    else if (t.type === "IDENTIFIER") tagClass = "token-IDENTIFIER";
    else if (t.type === "LPAREN" || t.type === "RPAREN") tagClass = "token-DELIM";

    row.innerHTML = `
      <td>${idx}</td>
      <td><span class="token-tag ${tagClass}">${t.type}</span></td>
      <td><strong>${t.value !== null ? t.value : ""}</strong></td>
      <td>${t.line} : ${t.column}</td>
      <td>${t.position}</td>
    `;
    tbodyTokens.appendChild(row);
  });
}

// Render AST Tree Visualizer
function renderAstTree(ast) {
  astTreeContainer.innerHTML = "";
  if (!ast) {
    astTreeContainer.innerHTML = `<p class="empty-state">No AST generated.</p>`;
    return;
  }

  function buildAstNode(node) {
    const div = document.createElement("div");
    div.className = `ast-node ast-node-${node.type}`;

    let labelHtml = `<strong>${node.type}</strong>`;
    if (node.value !== undefined) {
      labelHtml += `: <span style="color:#fff">${node.value}</span>`;
    }
    if (node.name !== undefined) {
      labelHtml += ` '${node.name}'`;
    }
    if (node.op !== undefined) {
      labelHtml += ` [${node.op}]`;
    }

    div.innerHTML = `<div class="ast-label">${labelHtml}</div>`;

    if (node.operand) {
      div.appendChild(buildAstNode(node.operand));
    }
    if (node.left) {
      div.appendChild(buildAstNode(node.left));
    }
    if (node.right) {
      div.appendChild(buildAstNode(node.right));
    }

    return div;
  }

  astTreeContainer.appendChild(buildAstNode(ast));
}

// Render RPN Chips
function renderRpnChips(rpnList) {
  rpnChipsContainer.innerHTML = "";
  if (!rpnList || rpnList.length === 0) {
    rpnChipsContainer.innerHTML = `<span class="empty-state">No RPN tokens available.</span>`;
    return;
  }

  rpnList.forEach((tokenStr, idx) => {
    const chip = document.createElement("div");
    chip.className = "rpn-token-chip";
    chip.innerHTML = `
      <span class="rpn-index">${idx}</span>
      <span>${tokenStr}</span>
    `;
    rpnChipsContainer.appendChild(chip);
  });
}

// Error Handling
function showError(errorData) {
  errorCard.classList.remove("hidden");
  errorType.textContent = errorData.error_type || "Evaluation Error";
  errorCoords.textContent = errorData.line ? `Line ${errorData.line} : Col ${errorData.column}` : "";
  errorMsg.textContent = errorData.message || "An unexpected error occurred.";

  if (errorData.diagnostic) {
    errorDiagnostic.textContent = errorData.diagnostic;
    errorDiagnostic.classList.remove("hidden");
  } else {
    errorDiagnostic.classList.add("hidden");
  }
}

function hideError() {
  errorCard.classList.add("hidden");
}
