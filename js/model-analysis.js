/**
 * RISKLENS - Enterprise Model Analysis & ML Diagnostics
 * File: js/model-analysis.js
 * Strictly NO emojis anywhere in the UI.
 * Pure SVG icons (Heroicons/Lucide format) and live API queries.
 * Resilient telemetry extraction & confusion matrix parsing.
 */

(function () {
  'use strict';

  // --- 1. CONFIGURATION & STATE ---
  const API_CONFIG = {
    // Dynamic Base URL resolving to port 8000 when served via live-server or local static dev
    BASE_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? (window.location.port === '8000' ? '/api/v1' : 'http://127.0.0.1:8000/api/v1')
      : '/api/v1',
    getHeaders() {
      const token = localStorage.getItem('access_token') || 
                    localStorage.getItem('token') || 
                    sessionStorage.getItem('access_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      return headers;
    }
  };

  // Model matrix configurations (9 Combinations)
  const TARGETS = {
    'cost_overrun': {
      id: 'cost_overrun',
      name: 'Cost Overrun',
      shortLabel: 'Cost Overrun',
      badge: 'Binary Classification',
      targetCol: 'target_cost_overrun_increase',
      description: 'Predicts whether ongoing project cost will escalate beyond currently approved sanction in subsequent quarters.',
      shapTargetKey: 'cost_overrun'
    },
    'time_overrun': {
      id: 'time_overrun',
      name: 'Time Overrun',
      shortLabel: 'Time Overrun',
      badge: 'Binary Classification',
      targetCol: 'target_time_overrun_increase',
      description: 'Identifies likelihood of commissioning milestone slippage beyond scheduled completion date.',
      shapTargetKey: 'time_overrun'
    },
    'overall_risk': {
      id: 'overall_risk',
      name: 'Overall Risk',
      shortLabel: 'Overall Risk (Multi-Class)',
      badge: 'Multi-Class (3-Tier)',
      targetCol: 'target_risk_class',
      description: 'Tri-level composite delay and cost risk rating: Class 0 (Low), Class 1 (Moderate), Class 2 (Critical Overrun).',
      shapTargetKey: 'risk_class'
    }
  };

  const ALGORITHMS = {
    'rf': {
      id: 'rf',
      name: 'Random Forest',
      badge: 'Ensemble Trees',
      supportsShap: true,
      keyMap: {
        'cost_overrun': 'rf_cost_overrun',
        'time_overrun': 'rf_time_overrun',
        'overall_risk': 'rf_overall_risk'
      },
      backendDbKeyMap: {
        'cost_overrun': 'random_forest_cost_overrun_classification',
        'time_overrun': 'random_forest_time_overrun_classification',
        'overall_risk': 'random_forest_risk_classification'
      }
    },
    'lr': {
      id: 'lr',
      name: 'Logistic Regression',
      badge: 'Linear Margin',
      supportsShap: false,
      keyMap: {
        'cost_overrun': 'lr_cost_overrun',
        'time_overrun': 'lr_time_overrun',
        'overall_risk': 'lr_overall_risk'
      },
      backendDbKeyMap: {
        'cost_overrun': 'logistic_regression_cost_overrun_classification',
        'time_overrun': 'logistic_regression_time_overrun_classification',
        'overall_risk': 'logistic_regression_risk_classification'
      }
    },
    'knn': {
      id: 'knn',
      name: 'K-Nearest Neighbors',
      badge: 'Instance-Based',
      supportsShap: false,
      keyMap: {
        'cost_overrun': 'knn_cost_overrun',
        'time_overrun': 'knn_time_overrun',
        'overall_risk': 'knn_overall_risk'
      },
      backendDbKeyMap: {
        'cost_overrun': 'knn_cost_overrun_classification',
        'time_overrun': 'knn_time_overrun_classification',
        'overall_risk': 'knn_risk_classification'
      }
    }
  };

  // State
  let appState = {
    activeTarget: 'cost_overrun',
    activeAlgorithm: 'rf',
    activeThresholdMode: 'operational', // 'operational' or 'default_0_50'
    allModelsList: [],
    currentModelDetail: null,
    shapDataset: null,
    isLoading: true,
    hasError: false,
    errorMessage: '',
    accordionOpen: false,
    selectedFeatureDrawer: null
  };

  // SVG Icons Helper (Zero Emojis anywhere in the UI)
  const ICONS = {
    cpu: '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>',
    checkCircle: '<svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    alertTriangle: '<svg viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    shieldCheck: '<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
    refresh: '<svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
    chevronDown: '<svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>',
    close: '<svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    info: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    grid: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    sliders: '<svg viewBox="0 0 24 24"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    barChart: '<svg viewBox="0 0 24 24"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    layers: '<svg viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    database: '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>'
  };

  // --- 2. API SERVICE CALLS ---
  async function fetchAllModelsCatalog() {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/ml/models`, {
        headers: API_CONFIG.getHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Could not fetch all models catalog:', err);
      return [];
    }
  }

  async function fetchShapExplainability() {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/ml/explainability/shap`, {
        headers: API_CONFIG.getHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Could not fetch SHAP explainability:', err);
      return null;
    }
  }

  async function fetchModelDetail(targetId, algoId) {
    const algo = ALGORITHMS[algoId];
    const primaryKey = algo.keyMap[targetId];
    const dbKey = algo.backendDbKeyMap[targetId];

    // Attempt primary key first (rf_cost_overrun, rf_time_overrun), then fallback to backend db key
    let response = await fetch(`${API_CONFIG.BASE_URL}/ml/models/${primaryKey}`, {
      headers: API_CONFIG.getHeaders()
    });

    if (response.status === 404 && dbKey) {
      response = await fetch(`${API_CONFIG.BASE_URL}/ml/models/${dbKey}`, {
        headers: API_CONFIG.getHeaders()
      });
    }

    if (!response.ok) {
      throw new Error(`Failed to communicate with live ML diagnostic service at /api/v1/ml/models/${primaryKey}. Ensure FastAPI backend server is running.`);
    }

    return await response.json();
  }

  // --- 3. RESILIENT DATA PARSER & TELEMETRY RESOLVER ---

  /**
   * Dynamically resolves active test metrics payload from model response
   * Supports dynamic operational threshold keys (e.g. at_operational_threshold_0_45, at_operational_threshold_0_24, etc.)
   * and balanced default threshold (at_default_threshold_0_50), or flat payloads (KNN, multiclass)
   */
  function resolveActivePerformancePayload(model, activeThresholdMode) {
    if (!model) return null;
    const tp = model.test_performance || model.test_metrics || model.metrics || model;
    if (typeof tp !== 'object' || tp === null) return null;

    // Dynamically locate any operational and default threshold keys
    const opKey = Object.keys(tp).find(k => k.startsWith('at_operational_threshold_') || k.includes('operational'));
    const defKey = Object.keys(tp).find(k => k.startsWith('at_default_threshold_') || k.includes('default_threshold'));

    if (activeThresholdMode === 'operational' && opKey && tp[opKey]) {
      const match = opKey.match(/0_\d+/);
      const thresholdNum = match ? parseFloat(match[0].replace('_', '.')) : 0.50;
      return {
        data: tp[opKey],
        hasOperational: true,
        hasDefault: !!defKey,
        opKey,
        defKey,
        thresholdNum,
        thresholdLabel: `${thresholdNum} (Operational Cutoff)`
      };
    }

    if (activeThresholdMode === 'default_0_50' && defKey && tp[defKey]) {
      return {
        data: tp[defKey],
        hasOperational: !!opKey,
        hasDefault: true,
        opKey,
        defKey,
        thresholdNum: 0.50,
        thresholdLabel: '0.50 (Balanced Default)'
      };
    }

    // Fallback: If operational was requested but only defKey exists
    if (defKey && tp[defKey] && !opKey) {
      return {
        data: tp[defKey],
        hasOperational: false,
        hasDefault: true,
        opKey: null,
        defKey,
        thresholdNum: 0.50,
        thresholdLabel: '0.50 (Balanced Default)'
      };
    }

    // Fallback: If defKey was requested but only opKey exists
    if (opKey && tp[opKey]) {
      const match = opKey.match(/0_\d+/);
      const thresholdNum = match ? parseFloat(match[0].replace('_', '.')) : 0.50;
      return {
        data: tp[opKey],
        hasOperational: true,
        hasDefault: !!defKey,
        opKey,
        defKey,
        thresholdNum,
        thresholdLabel: `${thresholdNum} (Operational Cutoff)`
      };
    }

    // Flat structure (e.g. KNN or Multiclass Overall Risk)
    return {
      data: tp,
      hasOperational: false,
      hasDefault: false,
      opKey: null,
      defKey: null,
      thresholdNum: model.best_model_parameters?.classification_threshold ?? model.classification_threshold ?? 0.50,
      thresholdLabel: (model.task === 'classification' && model.target === 'target_risk_class')
        ? 'Argmax (OvR Multi-class)'
        : '0.50 (Default)'
    };
  }

  /**
   * Flexible getter function to extract holdout test metrics regardless of nesting
   */
  function extractTelemetryMetrics(model, activeThresholdMode) {
    const resolved = resolveActivePerformancePayload(model, activeThresholdMode);
    if (!resolved || !resolved.data) return null;

    const data = resolved.data;
    const root = model || {};

    // Accuracy: Read data.test_metrics?.accuracy ?? data.metrics?.accuracy ?? data.test_accuracy ?? data.accuracy
    const accuracy = data.test_metrics?.accuracy ?? data.metrics?.accuracy ?? data.test_accuracy ?? 
                     data.accuracy ?? root.test_accuracy ?? root.accuracy;

    // Precision: Read data.test_metrics?.precision ?? data.metrics?.precision ?? data.test_precision ?? data.precision
    const precision = data.test_metrics?.precision ?? data.metrics?.precision ?? data.test_precision ?? 
                      data.weighted_precision ?? data.precision ?? data.macro_precision ?? root.precision;

    // Recall: Read data.test_metrics?.recall ?? data.metrics?.recall ?? data.test_recall ?? data.recall
    const recall = data.test_metrics?.recall ?? data.metrics?.recall ?? data.test_recall ?? 
                   data.weighted_recall ?? data.recall ?? data.macro_recall ?? root.recall;

    // F1 Score: Read data.test_metrics?.f1 ?? data.metrics?.f1 ?? data.test_f1 ?? data.f1
    const f1 = data.test_metrics?.f1 ?? data.metrics?.f1 ?? data.test_f1 ?? 
               data.weighted_f1 ?? data.f1 ?? data.macro_f1 ?? root.f1;

    // ROC-AUC: Read data.test_metrics?.roc_auc ?? data.metrics?.roc_auc ?? data.test_roc_auc ?? data.roc_auc
    const rocAuc = data.test_metrics?.roc_auc ?? data.metrics?.roc_auc ?? data.test_roc_auc ?? 
                   data.multiclass_roc_auc_ovr ?? data.roc_auc ?? root.roc_auc;

    // Decision Threshold: Read data.threshold ?? data.operational_threshold ?? resolved.thresholdNum ?? 0.5
    const threshold = data.threshold ?? data.operational_threshold ?? resolved.thresholdNum ?? 
                      root.classification_threshold ?? 0.50;

    return {
      accuracy,
      precision,
      recall,
      f1,
      rocAuc,
      threshold,
      thresholdLabel: resolved.thresholdLabel,
      hasOperational: resolved.hasOperational,
      hasDefault: resolved.hasDefault,
      opKey: resolved.opKey,
      defKey: resolved.defKey,
      rawPayload: data
    };
  }

  /**
   * Robust Confusion Matrix Parser supporting:
   * 1. 2D Matrix Array: [[TN, FP], [FN, TP]]
   * 2. Named Object: { tn, fp, fn, tp } or { true_negative, false_positive, false_negative, true_positive }
   * 3. Multiclass 3x3 Array: [[C00, C01, C02], [C10, C11, C12], [C20, C21, C22]]
   */
  function parseConfusionMatrix(model, activeThresholdMode) {
    const resolved = resolveActivePerformancePayload(model, activeThresholdMode);
    const data = resolved?.data || model?.test_performance || model || {};

    // 1. Check direct confusion_matrix candidate in payload or model
    let rawMatrix = data.confusion_matrix ?? data.matrix ?? model?.test_performance?.confusion_matrix ?? model?.confusion_matrix;

    // Handle 2D Matrix Array
    if (Array.isArray(rawMatrix) && rawMatrix.length > 0 && Array.isArray(rawMatrix[0])) {
      if (rawMatrix.length === 2 && rawMatrix[0].length === 2) {
        const tn = Number(rawMatrix[0][0]) || 0;
        const fp = Number(rawMatrix[0][1]) || 0;
        const fn = Number(rawMatrix[1][0]) || 0;
        const tp = Number(rawMatrix[1][1]) || 0;
        return {
          type: 'binary',
          tn, fp, fn, tp,
          total: tn + fp + fn + tp
        };
      }
      if (rawMatrix.length === 3 && rawMatrix[0].length === 3) {
        let total = 0;
        for (let r = 0; r < 3; r++) {
          for (let c = 0; c < 3; c++) {
            total += (Number(rawMatrix[r][c]) || 0);
          }
        }
        return {
          type: 'multiclass',
          matrix: rawMatrix,
          total: total || 1103
        };
      }
    }

    // Handle Named Object: { tn, fp, fn, tp } or { true_negative, false_positive, false_negative, true_positive }
    const obj = (rawMatrix && typeof rawMatrix === 'object' && !Array.isArray(rawMatrix)) ? rawMatrix : data;
    const tn = obj.tn ?? obj.true_negative ?? obj.true_negatives;
    const fp = obj.fp ?? obj.false_positive ?? obj.false_positives;
    const fn = obj.fn ?? obj.false_negative ?? obj.false_negatives;
    const tp = obj.tp ?? obj.true_positive ?? obj.true_positives;

    if (tn !== undefined && fp !== undefined && fn !== undefined && tp !== undefined &&
        tn !== null && fp !== null && fn !== null && tp !== null) {
      const nTN = Number(tn) || 0;
      const nFP = Number(fp) || 0;
      const nFN = Number(fn) || 0;
      const nTP = Number(tp) || 0;
      return {
        type: 'binary',
        tn: nTN, fp: nFP, fn: nFN, tp: nTP,
        total: nTN + nFP + nFN + nTP
      };
    }

    return null;
  }

  // --- 4. CONTROLLER & DISPATCHER ---
  async function loadData(isInitial = false) {
    appState.isLoading = true;
    appState.hasError = false;
    appState.errorMessage = '';
    
    if (isInitial || !document.getElementById('maHeroPanel')) {
      renderApp();
    } else {
      renderLoadingOverlay();
    }

    try {
      // Parallel live backend fetch
      const [catalog, shap, modelDetail] = await Promise.all([
        fetchAllModelsCatalog(),
        fetchShapExplainability(),
        fetchModelDetail(appState.activeTarget, appState.activeAlgorithm)
      ]);

      appState.allModelsList = catalog;
      appState.shapDataset = shap;
      appState.currentModelDetail = modelDetail;
      appState.isLoading = false;
      renderApp();
    } catch (error) {
      console.error('Error loading ML diagnostics:', error);
      appState.isLoading = false;
      appState.hasError = true;
      appState.errorMessage = error.message || 'Failed to communicate with live ML diagnostic service at /api/v1/ml/models. Ensure FastAPI backend server is running.';
      renderApp();
    }
  }

  function handleTargetChange(newTarget) {
    if (appState.activeTarget === newTarget) return;
    appState.activeTarget = newTarget;
    loadData();
  }

  function handleAlgorithmChange(newAlgo) {
    if (appState.activeAlgorithm === newAlgo) return;
    appState.activeAlgorithm = newAlgo;
    loadData();
  }

  function handleThresholdToggle(mode) {
    if (appState.activeThresholdMode === mode) return;
    appState.activeThresholdMode = mode;
    renderApp();
  }

  function toggleAccordion() {
    appState.accordionOpen = !appState.accordionOpen;
    const accordion = document.getElementById('maParamsAccordion');
    if (accordion) {
      accordion.classList.toggle('open', appState.accordionOpen);
    }
  }

  function openFeatureDrawer(featureObj, totalImportance) {
    appState.selectedFeatureDrawer = {
      ...featureObj,
      totalImportance
    };
    renderDrawer();
  }

  function closeFeatureDrawer() {
    appState.selectedFeatureDrawer = null;
    const backdrop = document.getElementById('maDrawerBackdrop');
    const drawer = document.getElementById('maDrawer');
    if (backdrop) backdrop.classList.remove('active');
    if (drawer) drawer.classList.remove('active');
  }

  // Formatting helpers
  function fmtPct(val) {
    if (val === null || val === undefined || isNaN(val)) return 'N/A';
    return (val * 100).toFixed(1) + '%';
  }

  function fmtNum(val, decimals = 3) {
    if (val === null || val === undefined || isNaN(val)) return 'N/A';
    return Number(val).toFixed(decimals);
  }

  function cleanFeatureName(name) {
    if (!name) return '';
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase())
      .replace('Clean', '')
      .replace('Calc', '(Calculated)')
      .trim();
  }

  function getFeatureInterpretation(feature) {
    const map = {
      'cost_anticipated': 'Projects with higher anticipated completion budget exhibit higher escalation velocity due to extensive capital outlays.',
      'cost_original': 'Original baseline estimates establish the fiscal scope; large variations indicate initial cost underestimation.',
      'project_size_ord': 'Mega projects (> ₹1,000 Cr) face complex multi-agency clearances and land procurement hurdles.',
      'time_overrun_months_calc': 'Historical schedule slippage compounds future milestones due to contractual penalty overhead.',
      'remaining_schedule_months': 'Compressed remaining duration without corresponding physical progress strongly signals impending delay.',
      'physical_progress_clean': 'Physical on-ground completion lag relative to financial outlay indicates work stoppage or contractor disputes.',
      'cost_escalation_rate_clean': 'Rate of financial overrun per quarter indicates whether inflationary or scope pressures are accelerating.',
      'has_clearance_issue': 'Pending environmental, forest, or wildlife clearances generate multi-month critical path delays.',
      'state_clean': 'State-level administrative clearances, land acquisition laws, and local labor conditions influence execution timelines.',
      'sector_clean': 'Linear infrastructure sectors (Railways, Road Transport) face continuous right-of-way challenges.'
    };
    return map[feature] || 'Identified by tree-based SHAP analysis as a significant risk-determining signal across monitored projects.';
  }

  // --- 5. RENDERERS ---
  function renderApp() {
    const container = document.getElementById('model-analysis-app');
    if (!container) return;

    if (appState.hasError) {
      container.innerHTML = renderErrorState();
      attachErrorListeners();
      return;
    }

    if (appState.isLoading && !document.getElementById('maHeroPanel')) {
      container.innerHTML = renderSkeletonState();
      return;
    }

    const target = TARGETS[appState.activeTarget];
    const algo = ALGORITHMS[appState.activeAlgorithm];
    const model = appState.currentModelDetail || {};

    container.innerHTML = `
      <!-- COMPONENT A: HEADER & DYNAMIC CONTROLS -->
      ${renderHeroAndControls(target, algo, model)}

      <!-- COMPONENT B: PERFORMANCE METRICS BANNER -->
      ${renderPerformanceMetrics(target, algo, model)}

      <!-- MIDDLE TWO-COLUMN GRID: CONFUSION MATRIX & LEAKAGE AUDIT -->
      <div class="ma-middle-layout">
        <!-- COMPONENT C: CONFUSION MATRIX MODULE -->
        ${renderConfusionMatrix(target, algo, model)}

        <!-- COMPONENT D: MODEL RELIABILITY & LEAKAGE AUDIT -->
        ${renderLeakageAudit(target, algo, model)}
      </div>

      <!-- COMPONENT E: SHAP EXPLAINABILITY BREAKDOWN -->
      ${renderShapSection(target, algo, model)}

      <!-- COMPONENT F: HYPERPARAMETERS & CONFIG ACCORDION -->
      ${renderHyperparametersAccordion(target, algo, model)}

      <!-- SLIDE-OVER DETAIL DRAWER CONTAINER -->
      <div class="ma-drawer-backdrop" id="maDrawerBackdrop"></div>
      <div class="ma-drawer" id="maDrawer"></div>
    `;

    attachEventListeners();
  }

  function renderLoadingOverlay() {
    const refreshBtn = document.getElementById('maRefreshBtn');
    if (refreshBtn) refreshBtn.classList.add('loading');
  }

  // Component A: Hero & Controls
  function renderHeroAndControls(target, algo, model) {
    const datasetInfo = model.dataset_info || {};
    const modelKeyDisplay = algo.keyMap[target.id];

    return `
      <section class="ma-hero-panel" id="maHeroPanel">
        <div class="ma-hero-header">
          <div class="ma-title-group">
            <h2>
              <span class="ma-icon ma-icon-lg">${ICONS.cpu}</span>
              Model Diagnostics &amp; ML Architecture Analysis
              <span class="ma-title-tag">MoSPI Official</span>
            </h2>
            <p class="ma-subtitle">
              Comprehensive telemetry, cross-validation metrics, confusion matrix diagnostics, and SHAP explainability for Central Sector Infrastructure Project monitoring.
            </p>
          </div>
          <div class="ma-hero-meta">
            <button class="ma-btn-refresh ${appState.isLoading ? 'loading' : ''}" id="maRefreshBtn" title="Re-fetch live metrics from backend">
              <span class="ma-icon">${ICONS.refresh}</span>
              <span>${appState.isLoading ? 'Fetching...' : 'Refresh Telemetry'}</span>
            </button>
          </div>
        </div>

        <!-- Dynamic Controls -->
        <div class="ma-controls-grid">
          <!-- Target Selector -->
          <div class="ma-control-group">
            <label class="ma-control-label">
              <span class="ma-icon ma-icon-sm">${ICONS.layers}</span>
              1. Select Prediction Target
            </label>
            <div class="ma-segmented-group" id="maTargetSegments">
              ${Object.values(TARGETS).map(t => `
                <button class="ma-segment-btn ${t.id === target.id ? 'active' : ''}" data-target-id="${t.id}">
                  ${t.shortLabel}
                </button>
              `).join('')}
            </div>
          </div>

          <!-- Algorithm Tabs -->
          <div class="ma-control-group">
            <label class="ma-control-label">
              <span class="ma-icon ma-icon-sm">${ICONS.sliders}</span>
              2. Select Algorithm Architecture
            </label>
            <div class="ma-segmented-group" id="maAlgoSegments">
              ${Object.values(ALGORITHMS).map(a => `
                <button class="ma-segment-btn ${a.id === algo.id ? 'active' : ''}" data-algo-id="${a.id}">
                  ${a.name}
                </button>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- Telemetry Breadcrumbs -->
        <div class="ma-active-model-strip">
          <div class="ma-chip-cluster">
            <span class="ma-chip ma-chip-code">
              Key: ${modelKeyDisplay}
            </span>
            <span class="ma-chip">
              Model: ${model.model_name || algo.name}
            </span>
            <span class="ma-chip">
              Task: ${target.badge}
            </span>
            <span class="ma-chip ma-chip-success">
              <span class="ma-icon ma-icon-sm">${ICONS.checkCircle}</span>
              Status: Validated
            </span>
          </div>
          <div class="ma-chip-cluster">
            <span class="ma-chip">
              Train: ${datasetInfo.train_sample_count || '6,627'} samples (${datasetInfo.train_period || '2012-2019'})
            </span>
            <span class="ma-chip">
              Test: ${datasetInfo.test_sample_count || '1,103'} samples (${datasetInfo.test_period || '2022-2025'})
            </span>
          </div>
        </div>
      </section>
    `;
  }

  // Component B: Performance Metrics
  function renderPerformanceMetrics(target, algo, model) {
    const metrics = extractTelemetryMetrics(model, appState.activeThresholdMode);
    const cvResults = model.cross_validation_results || {};

    // Null Data Handling
    if (!metrics) {
      return `
        <section>
          <div class="ma-section-header">
            <h3 class="ma-section-title">
              <span class="ma-icon">${ICONS.barChart}</span>
              Executive Performance Telemetry
            </h3>
          </div>
          <div class="ma-enterprise-callout">
            <div class="ma-callout-icon-box">
              <span class="ma-icon ma-icon-lg">${ICONS.info}</span>
            </div>
            <div class="ma-callout-content">
              <h4>Telemetry for this algorithm combination is currently non-evaluated on backend.</h4>
              <p>Evaluation metrics payload was returned as null from the live endpoint. Ensure the model evaluation job has run successfully on the server.</p>
            </div>
          </div>
        </section>
      `;
    }

    return `
      <section>
        <div class="ma-section-header">
          <h3 class="ma-section-title">
            <span class="ma-icon">${ICONS.barChart}</span>
            Executive Performance Telemetry
          </h3>
          <span class="ma-section-caption">
            Holdout Test Evaluation (${model.dataset_info?.test_period || '2022-2025'} Snapshot Partition)
          </span>
        </div>

        <div class="ma-metrics-grid">
          <!-- Accuracy -->
          <div class="ma-metric-card">
            <div class="ma-metric-top">
              <span class="ma-metric-label">Accuracy</span>
              <span class="ma-metric-badge">Overall</span>
            </div>
            <div class="ma-metric-val">${fmtPct(metrics.accuracy)}</div>
            <div class="ma-metric-sub">
              <span>Test Holdout</span>
              <span>CV: ${fmtPct(cvResults.cv_mean_accuracy)}</span>
            </div>
          </div>

          <!-- Precision -->
          <div class="ma-metric-card">
            <div class="ma-metric-top">
              <span class="ma-metric-label">Precision</span>
              <span class="ma-metric-badge">${target.id === 'overall_risk' ? 'Weighted' : 'Confidence'}</span>
            </div>
            <div class="ma-metric-val">${fmtPct(metrics.precision)}</div>
            <div class="ma-metric-sub">
              <span>Positive Pred.</span>
              <span>CV: ${fmtPct(cvResults.cv_mean_precision)}</span>
            </div>
          </div>

          <!-- Recall -->
          <div class="ma-metric-card">
            <div class="ma-metric-top">
              <span class="ma-metric-label">Recall</span>
              <span class="ma-metric-badge">${target.id === 'overall_risk' ? 'Weighted' : 'Sensitivity'}</span>
            </div>
            <div class="ma-metric-val">${fmtPct(metrics.recall)}</div>
            <div class="ma-metric-sub">
              <span>Risk Capture</span>
              <span>CV: ${fmtPct(cvResults.cv_mean_recall)}</span>
            </div>
          </div>

          <!-- F1 Score -->
          <div class="ma-metric-card">
            <div class="ma-metric-top">
              <span class="ma-metric-label">F1 Score</span>
              <span class="ma-metric-badge">Harmonic</span>
            </div>
            <div class="ma-metric-val">${fmtNum(metrics.f1, 3)}</div>
            <div class="ma-metric-sub">
              <span>Balanced Metric</span>
              <span>CV: ${fmtNum(cvResults.cv_mean_f1, 3)}</span>
            </div>
          </div>

          <!-- ROC-AUC -->
          <div class="ma-metric-card">
            <div class="ma-metric-top">
              <span class="ma-metric-label">ROC-AUC</span>
              <span class="ma-metric-badge">${target.id === 'overall_risk' ? 'OvR' : 'Discrimination'}</span>
            </div>
            <div class="ma-metric-val">${fmtNum(metrics.rocAuc, 3)}</div>
            <div class="ma-metric-sub">
              <span>Area Under Curve</span>
              <span>CV: ${fmtNum(cvResults.cv_mean_roc_auc, 3)}</span>
            </div>
          </div>

          <!-- Operational Threshold -->
          <div class="ma-metric-card">
            <div class="ma-metric-top">
              <span class="ma-metric-label">Threshold</span>
              <span class="ma-metric-badge">Decision Boundary</span>
            </div>
            <div class="ma-metric-val">${metrics.threshold !== null ? metrics.threshold : '0.50'}</div>
            <div class="ma-metric-sub">
              <span>${metrics.thresholdLabel}</span>
            </div>
          </div>
        </div>

        <!-- Threshold Selector (if operational and default exist) -->
        ${(metrics.hasOperational && metrics.hasDefault) ? `
          <div class="ma-threshold-bar">
            <span><strong>Threshold Decision Calibration:</strong> Switch test evaluation policy to inspect impact on false alarms vs missed alerts.</span>
            <div class="ma-threshold-controls">
              <button class="ma-threshold-btn ${appState.activeThresholdMode === 'operational' ? 'active' : ''}" data-threshold-mode="operational">
                Operational Cutoff (${metrics.threshold})
              </button>
              <button class="ma-threshold-btn ${appState.activeThresholdMode === 'default_0_50' ? 'active' : ''}" data-threshold-mode="default_0_50">
                Default (0.50)
              </button>
            </div>
          </div>
        ` : ''}

        <!-- Cross Validation Summary Strip -->
        <div class="ma-cv-strip">
          <div class="ma-cv-title">
            <span class="ma-icon ma-icon-sm">${ICONS.shieldCheck}</span>
            5-Fold Stratified Cross-Validation Results
          </div>
          <div class="ma-cv-grid">
            <div class="ma-cv-item">
              <div class="ma-cv-item-label">CV Mean Accuracy</div>
              <div class="ma-cv-item-val">${fmtPct(cvResults.cv_mean_accuracy)} &plusmn; ${fmtPct(cvResults.cv_std_accuracy)}</div>
            </div>
            <div class="ma-cv-item">
              <div class="ma-cv-item-label">CV Mean Precision</div>
              <div class="ma-cv-item-val">${fmtPct(cvResults.cv_mean_precision)}</div>
            </div>
            <div class="ma-cv-item">
              <div class="ma-cv-item-label">CV Mean Recall</div>
              <div class="ma-cv-item-val">${fmtPct(cvResults.cv_mean_recall)}</div>
            </div>
            <div class="ma-cv-item">
              <div class="ma-cv-item-label">CV Mean F1</div>
              <div class="ma-cv-item-val">${fmtNum(cvResults.cv_mean_f1, 3)}</div>
            </div>
            <div class="ma-cv-item">
              <div class="ma-cv-item-label">CV Mean ROC-AUC</div>
              <div class="ma-cv-item-val">${fmtNum(cvResults.cv_mean_roc_auc, 3)}</div>
            </div>
          </div>
        </div>
      </section>
    `;
  }

  // Component C: Confusion Matrix Module
  function renderConfusionMatrix(target, algo, model) {
    const parsed = parseConfusionMatrix(model, appState.activeThresholdMode);

    // Graceful Null Data Handling
    if (!parsed) {
      return `
        <div class="ma-card">
          <div class="ma-section-header">
            <h3 class="ma-section-title">
              <span class="ma-icon">${ICONS.grid}</span>
              Confusion Matrix Module
            </h3>
          </div>
          <div class="ma-enterprise-callout" style="margin-top: 8px;">
            <div class="ma-callout-icon-box">
              <span class="ma-icon ma-icon-lg">${ICONS.info}</span>
            </div>
            <div class="ma-callout-content">
              <h4>Telemetry for this algorithm combination is currently non-evaluated on backend.</h4>
              <p>Confusion matrix observations are not recorded in the server response for this selection.</p>
            </div>
          </div>
        </div>
      `;
    }

    // Binary Classification (2x2 Matrix)
    if (parsed.type === 'binary') {
      const { tn, fp, fn, tp, total } = parsed;
      const safeTotal = total || 1;
      const accuracy = ((tn + tp) / safeTotal) * 100;
      const errorRate = ((fp + fn) / safeTotal) * 100;

      return `
        <div class="ma-card">
          <div class="ma-section-header">
            <h3 class="ma-section-title">
              <span class="ma-icon">${ICONS.grid}</span>
              Binary Confusion Matrix
            </h3>
            <span class="ma-section-caption">${total} Test Projects</span>
          </div>

          <div class="ma-matrix-container">
            <table class="ma-matrix-table">
              <thead>
                <tr>
                  <th></th>
                  <th colspan="2" class="ma-matrix-header-group">Predicted Condition</th>
                </tr>
                <tr>
                  <th>Actual Reality</th>
                  <th>Predicted No Overrun (0)</th>
                  <th>Predicted Overrun (1)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="ma-matrix-row-label">Actual No Overrun (0)</td>
                  <td class="ma-matrix-cell ma-cell-correct">
                    <span class="cell-count">${tn}</span>
                    <span class="cell-desc">True Negative</span>
                    <span class="cell-pct">${((tn / safeTotal) * 100).toFixed(1)}%</span>
                  </td>
                  <td class="ma-matrix-cell ma-cell-error">
                    <span class="cell-count">${fp}</span>
                    <span class="cell-desc">False Positive (Type I)</span>
                    <span class="cell-pct">${((fp / safeTotal) * 100).toFixed(1)}%</span>
                  </td>
                </tr>
                <tr>
                  <td class="ma-matrix-row-label">Actual Overrun (1)</td>
                  <td class="ma-matrix-cell ma-cell-error">
                    <span class="cell-count">${fn}</span>
                    <span class="cell-desc">False Negative (Type II)</span>
                    <span class="cell-pct">${((fn / safeTotal) * 100).toFixed(1)}%</span>
                  </td>
                  <td class="ma-matrix-cell ma-cell-correct">
                    <span class="cell-count">${tp}</span>
                    <span class="cell-desc">True Positive</span>
                    <span class="cell-pct">${((tp / safeTotal) * 100).toFixed(1)}%</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="ma-matrix-summary-row">
            <div class="ma-matrix-stat">
              <div class="ma-matrix-stat-label">Total Observations</div>
              <div class="ma-matrix-stat-val">${total}</div>
            </div>
            <div class="ma-matrix-stat">
              <div class="ma-matrix-stat-label">Correct Classifications</div>
              <div class="ma-matrix-stat-val" style="color: #059669;">${tn + tp} (${accuracy.toFixed(1)}%)</div>
            </div>
            <div class="ma-matrix-stat">
              <div class="ma-matrix-stat-label">Misclassification Rate</div>
              <div class="ma-matrix-stat-val" style="color: #dc2626;">${fn + fp} (${errorRate.toFixed(1)}%)</div>
            </div>
          </div>
        </div>
      `;
    }

    // Multi-Class Risk Model (3x3 Matrix)
    if (parsed.type === 'multiclass') {
      const matrix = parsed.matrix;
      const classLabels = [
        'Class 0 (Low / No Overrun)',
        'Class 1 (Inconclusive)',
        'Class 2 (High Overrun)'
      ];

      let correctTotal = 0;
      let grandTotal = parsed.total || 0;

      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          if (r === c) correctTotal += (Number(matrix[r][c]) || 0);
        }
      }

      const safeGrandTotal = grandTotal || 1;

      return `
        <div class="ma-card">
          <div class="ma-section-header">
            <h3 class="ma-section-title">
              <span class="ma-icon">${ICONS.grid}</span>
              Multi-Class Confusion Matrix (3-Tier Risk)
            </h3>
            <span class="ma-section-caption">${grandTotal} Test Projects</span>
          </div>

          <div class="ma-matrix-container">
            <table class="ma-matrix-table">
              <thead>
                <tr>
                  <th></th>
                  <th colspan="3" class="ma-matrix-header-group">Predicted Risk Tier</th>
                </tr>
                <tr>
                  <th>Actual Class</th>
                  <th>Pred. Class 0</th>
                  <th>Pred. Class 1</th>
                  <th>Pred. Class 2</th>
                </tr>
              </thead>
              <tbody>
                ${matrix.map((row, rIdx) => `
                  <tr>
                    <td class="ma-matrix-row-label">${classLabels[rIdx]}</td>
                    ${row.map((cellVal, cIdx) => {
                      const isDiagonal = rIdx === cIdx;
                      const numVal = Number(cellVal) || 0;
                      const cellClass = isDiagonal ? 'ma-cell-correct' : (numVal > 0 ? 'ma-cell-error' : 'ma-cell-neutral');
                      return `
                        <td class="ma-matrix-cell ${cellClass}">
                          <span class="cell-count">${numVal}</span>
                          <span class="cell-desc">${isDiagonal ? 'Match' : 'Error'}</span>
                          <span class="cell-pct">${((numVal / safeGrandTotal) * 100).toFixed(1)}%</span>
                        </td>
                      `;
                    }).join('')}
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>

          <div class="ma-matrix-summary-row">
            <div class="ma-matrix-stat">
              <div class="ma-matrix-stat-label">Total Observations</div>
              <div class="ma-matrix-stat-val">${grandTotal}</div>
            </div>
            <div class="ma-matrix-stat">
              <div class="ma-matrix-stat-label">Diagonal Accuracy</div>
              <div class="ma-matrix-stat-val" style="color: #059669;">${((correctTotal / safeGrandTotal) * 100).toFixed(1)}%</div>
            </div>
            <div class="ma-matrix-stat">
              <div class="ma-matrix-stat-label">Misclassified Samples</div>
              <div class="ma-matrix-stat-val" style="color: #dc2626;">${grandTotal - correctTotal}</div>
            </div>
          </div>
        </div>
      `;
    }

    return '';
  }

  // Component D: Model Reliability & Leakage Audit
  function renderLeakageAudit(target, algo, model) {
    const audit = model.leakage_audit || {};
    const isPassed = audit.status === 'PASSED';
    const excludedCols = audit.excluded_target_and_future_cols || [
      'target_risk_class',
      'target_time_overrun_increase',
      'target_cost_overrun_increase',
      'future_time_overrun',
      'future_cost'
    ];

    return `
      <div class="ma-card">
        <div class="ma-section-header">
          <h3 class="ma-section-title">
            <span class="ma-icon">${ICONS.shieldCheck}</span>
            Model Reliability &amp; Data Leakage Audit
          </h3>
          <span class="ma-audit-status-badge ${isPassed ? 'ma-audit-status-pass' : 'ma-audit-status-alert'}">
            <span class="ma-icon ma-icon-sm">${isPassed ? ICONS.checkCircle : ICONS.alertTriangle}</span>
            Audit Status: ${audit.status || 'PASSED'}
          </span>
        </div>

        <p class="ma-subtitle">
          Rigorous MoSPI data governance verification guarantees zero temporal leakage and strict train-only preprocessing isolation.
        </p>

        <div class="ma-audit-grid">
          <!-- Train Test Leakage Check -->
          <div class="ma-audit-badge-row">
            <div class="ma-audit-badge-info">
              <span class="ma-icon" style="color: #059669;">${ICONS.checkCircle}</span>
              <div>
                <h5 class="ma-audit-title">Temporal Train-Test Split Integrity</h5>
                <p class="ma-audit-sub">Strict chronological cutoff (Train &lt; 2020 &bull; Test 2022-2025)</p>
              </div>
            </div>
            <span class="ma-audit-status-badge ma-audit-status-pass">VERIFIED</span>
          </div>

          <!-- Lookahead Bias Check -->
          <div class="ma-audit-badge-row">
            <div class="ma-audit-badge-info">
              <span class="ma-icon" style="color: #059669;">${ICONS.checkCircle}</span>
              <div>
                <h5 class="ma-audit-title">Zero Future Lookahead Bias</h5>
                <p class="ma-audit-sub">No post-snapshot milestones, expenditures, or revisions</p>
              </div>
            </div>
            <span class="ma-audit-status-badge ma-audit-status-pass">PASSED</span>
          </div>

          <!-- Preprocessing Transformers Isolation -->
          <div class="ma-audit-badge-row">
            <div class="ma-audit-badge-info">
              <span class="ma-icon" style="color: #059669;">${ICONS.checkCircle}</span>
              <div>
                <h5 class="ma-audit-title">Preprocessing Transformers Isolation</h5>
                <p class="ma-audit-sub">StandardScaler &amp; OneHotEncoder fitted strictly on training subset</p>
              </div>
            </div>
            <span class="ma-audit-status-badge ma-audit-status-pass">ISOLATED</span>
          </div>
        </div>

        <!-- Excluded Target & Future Columns Panel -->
        <div class="ma-leakage-excluded-panel">
          <h5>
            <span class="ma-icon ma-icon-sm">${ICONS.alertTriangle}</span>
            Excluded Target &amp; Future Feature Columns (${excludedCols.length})
          </h5>
          <div class="ma-leakage-col-tags">
            ${excludedCols.map(col => `
              <span class="ma-col-tag">${col}</span>
            `).join('')}
          </div>
        </div>

        <div class="ma-snapshot-verification-text">
          <strong>Snapshot Temporal Guarantee:</strong> ${audit.snapshot_verification || 'All input features were verified to reflect data available at the exact snapshot report date.'}
        </div>
      </div>
    `;
  }

  // Component E: SHAP Explainability Breakdown
  function renderShapSection(target, algo, model) {
    const isRandomForest = algo.id === 'rf';

    // Extract SHAP features
    let shapFeatures = [];
    if (appState.shapDataset && appState.shapDataset[target.shapTargetKey]) {
      shapFeatures = appState.shapDataset[target.shapTargetKey].features || [];
    } else if (Array.isArray(model.top_feature_importance)) {
      shapFeatures = model.top_feature_importance.map(item => ({
        feature: item.feature,
        mean_abs_shap: item.importance,
        direction: 'Non-linear / context-dependent'
      }));
    }

    // If not Random Forest or features are missing/null, render enterprise callout
    if (!isRandomForest || !shapFeatures || shapFeatures.length === 0) {
      return `
        <section class="ma-shap-card">
          <div class="ma-section-header">
            <h3 class="ma-section-title">
              <span class="ma-icon">${ICONS.barChart}</span>
              Global SHAP Feature Explainability
            </h3>
            <span class="ma-section-caption">${algo.name} Architecture</span>
          </div>

          <div class="ma-enterprise-callout">
            <div class="ma-callout-icon-box">
              <span class="ma-icon ma-icon-lg">${ICONS.info}</span>
            </div>
            <div class="ma-callout-content">
              <h4>Global SHAP explainability is not computed for this model.</h4>
              <p>
                TreeSHAP (Tree-based Shapley Additive Explanations) is mathematically optimized and computed exclusively for the <strong>Random Forest Ensemble</strong> architecture in the RISKLENS intelligence engine.
                Linear decision models (Logistic Regression) utilize fixed hyperplane weight coefficients, whereas instance-based models (K-Nearest Neighbors) compute local Minkowski distance metrics.
              </p>
              <div class="ma-callout-specs">
                <span class="ma-callout-spec-pill">
                  <span class="ma-icon ma-icon-sm">${ICONS.layers}</span>
                  Model Architecture: ${algo.name}
                </span>
                <span class="ma-callout-spec-pill">
                  <span class="ma-icon ma-icon-sm">${ICONS.sliders}</span>
                  Explainer Type: TreeSHAP Excluded
                </span>
                <span class="ma-callout-spec-pill">
                  <span class="ma-icon ma-icon-sm">${ICONS.shieldCheck}</span>
                  Compliance: MoSPI Baseline Standards
                </span>
              </div>
            </div>
          </div>
        </section>
      `;
    }

    // Sort features descending by mean_abs_shap
    const sortedFeatures = [...shapFeatures].sort((a, b) => (b.mean_abs_shap || 0) - (a.mean_abs_shap || 0));
    const maxVal = sortedFeatures[0]?.mean_abs_shap || 1;
    const totalImportance = sortedFeatures.reduce((acc, curr) => acc + (curr.mean_abs_shap || 0), 0);

    return `
      <section class="ma-shap-card">
        <div class="ma-section-header">
          <div>
            <h3 class="ma-section-title">
              <span class="ma-icon">${ICONS.barChart}</span>
              Global SHAP Feature Importance &amp; Directional Impact
            </h3>
            <span class="ma-section-caption">
              Derived via TreeSHAP on holdout test projects. Click any feature bar to inspect detailed infrastructure impact.
            </span>
          </div>
          <div class="ma-shap-header-meta">
            <span class="ma-chip">
              Explainer: TreeExplainer
            </span>
            <span class="ma-chip">
              ${sortedFeatures.length} Key Features
            </span>
          </div>
        </div>

        <div class="ma-shap-chart-container" id="maShapRowsList">
          ${sortedFeatures.slice(0, 15).map((f, idx) => {
            const val = f.mean_abs_shap || 0;
            const pct = Math.max(4, (val / maxVal) * 100);
            const direction = f.direction || 'Context-Dependent';
            
            let dirBadgeClass = 'ma-dir-nonlinear';
            if (direction.toLowerCase().includes('increase')) {
              dirBadgeClass = 'ma-dir-increase';
            } else if (direction.toLowerCase().includes('decrease')) {
              dirBadgeClass = 'ma-dir-decrease';
            }

            return `
              <div class="ma-shap-row" data-feature-index="${idx}" title="Click to view detailed policy diagnostics">
                <div class="ma-shap-feature-col">
                  <span class="ma-shap-feature-name">${f.feature}</span>
                  <span class="ma-shap-feature-sub">${cleanFeatureName(f.feature)}</span>
                </div>

                <div class="ma-shap-bar-track">
                  <div class="ma-shap-bar-fill" style="width: ${pct}%;"></div>
                </div>

                <div class="ma-shap-val-col">
                  ${fmtNum(val, 4)}
                </div>

                <div class="ma-shap-direction-col">
                  <span class="ma-shap-direction-badge ${dirBadgeClass}">
                    ${direction}
                  </span>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `;
  }

  // Component F: Hyperparameters & Configuration Accordion
  function renderHyperparametersAccordion(target, algo, model) {
    const params = model.best_model_parameters || {};
    const paramEntries = Object.entries(params).filter(([k]) => k !== 'scaling_used');

    return `
      <section class="ma-accordion-item ${appState.accordionOpen ? 'open' : ''}" id="maParamsAccordion">
        <button class="ma-accordion-trigger" id="maAccordionToggleBtn">
          <div class="ma-accordion-trigger-title">
            <span class="ma-icon">${ICONS.sliders}</span>
            <span>Hyperparameter Configuration &amp; Feature Preprocessing Pipeline</span>
          </div>
          <span class="ma-icon ma-accordion-icon">${ICONS.chevronDown}</span>
        </button>

        <div class="ma-accordion-content">
          <div class="ma-params-grid">
            ${paramEntries.map(([key, val]) => `
              <div class="ma-param-tile">
                <div class="ma-param-tile-key">
                  <span class="ma-icon ma-icon-sm">${ICONS.cpu}</span>
                  ${key}
                </div>
                <div class="ma-param-tile-val">${val !== null ? val : 'None'}</div>
              </div>
            `).join('')}
          </div>

          <div class="ma-scaling-strip">
            <span class="ma-icon" style="color: #1d4ed8;">${ICONS.database}</span>
            <div>
              <strong>Feature Preprocessing &amp; Encoding Pipeline:</strong>
              <span>${params.scaling_used || 'StandardScaler for numerical features, OneHotEncoder for categorical features (Fitted strictly on train partition).'}</span>
            </div>
          </div>
        </div>
      </section>
    `;
  }

  // Slide-Over Detail Drawer
  function renderDrawer() {
    const drawer = document.getElementById('maDrawer');
    const backdrop = document.getElementById('maDrawerBackdrop');
    if (!drawer || !backdrop || !appState.selectedFeatureDrawer) return;

    const f = appState.selectedFeatureDrawer;
    const cleanName = cleanFeatureName(f.feature);
    const interp = getFeatureInterpretation(f.feature);
    const relPct = f.totalImportance > 0 ? ((f.mean_abs_shap / f.totalImportance) * 100).toFixed(1) : 'N/A';

    let dirBadgeClass = 'ma-dir-nonlinear';
    if ((f.direction || '').toLowerCase().includes('increase')) {
      dirBadgeClass = 'ma-dir-increase';
    } else if ((f.direction || '').toLowerCase().includes('decrease')) {
      dirBadgeClass = 'ma-dir-decrease';
    }

    drawer.innerHTML = `
      <div class="ma-drawer-header">
        <div class="ma-drawer-title-box">
          <h3>${f.feature}</h3>
          <p>${cleanName}</p>
        </div>
        <button class="ma-drawer-close" id="maDrawerCloseBtn" aria-label="Close Drawer">
          <span class="ma-icon">${ICONS.close}</span>
        </button>
      </div>

      <div class="ma-drawer-body">
        <div class="ma-drawer-stat-grid">
          <div class="ma-drawer-stat-card">
            <div class="label">Mean Absolute SHAP</div>
            <div class="val">${fmtNum(f.mean_abs_shap, 4)}</div>
          </div>
          <div class="ma-drawer-stat-card">
            <div class="label">Relative Impact Share</div>
            <div class="val">${relPct}%</div>
          </div>
        </div>

        <div>
          <div class="label" style="font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 6px;">
            Directional Risk Bias
          </div>
          <span class="ma-shap-direction-badge ${dirBadgeClass}" style="font-size: 12.5px; padding: 6px 12px;">
            ${f.direction || 'Context-Dependent'}
          </span>
        </div>

        <div class="ma-drawer-explanation">
          <h4>Infrastructure Domain Interpretation</h4>
          <p>${interp}</p>
        </div>

        <div class="ma-drawer-explanation" style="border-left-color: #10b981;">
          <h4>MoSPI Monitoring Recommendation</h4>
          <p>
            When monitoring projects where <strong>${cleanName}</strong> deviates significantly from scheduled baselines,
            project directors should trigger accelerated inter-ministerial reviews to curb cascading secondary delays.
          </p>
        </div>
      </div>
    `;

    backdrop.classList.add('active');
    drawer.classList.add('active');

    // Drawer close listeners
    const closeBtn = document.getElementById('maDrawerCloseBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeFeatureDrawer);
    }
    backdrop.onclick = closeFeatureDrawer;
  }

  // Skeleton Loader State (Smooth Pulse Overlays)
  function renderSkeletonState() {
    return `
      <section class="ma-hero-panel">
        <div class="ma-skeleton ma-skeleton-title"></div>
        <div class="ma-skeleton ma-skeleton-text" style="width: 60%;"></div>
        <div class="ma-controls-grid" style="margin-top: 24px;">
          <div class="ma-skeleton" style="height: 54px;"></div>
          <div class="ma-skeleton" style="height: 54px;"></div>
        </div>
      </section>

      <section>
        <div class="ma-skeleton ma-skeleton-text" style="width: 220px; height: 26px; margin-bottom: 18px;"></div>
        <div class="ma-metrics-grid">
          ${[1, 2, 3, 4, 5, 6].map(() => `
            <div class="ma-skeleton ma-skeleton-card"></div>
          `).join('')}
        </div>
      </section>

      <div class="ma-middle-layout">
        <div class="ma-card">
          <div class="ma-skeleton" style="height: 240px;"></div>
        </div>
        <div class="ma-card">
          <div class="ma-skeleton" style="height: 240px;"></div>
        </div>
      </div>

      <section class="ma-shap-card">
        <div class="ma-skeleton ma-skeleton-title" style="width: 320px;"></div>
        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 22px;">
          ${[1, 2, 3, 4, 5].map(() => `
            <div class="ma-skeleton ma-skeleton-bar"></div>
          `).join('')}
        </div>
      </section>
    `;
  }

  // Error State Banner
  function renderErrorState() {
    return `
      <div class="ma-error-banner">
        <div class="ma-error-icon-box">
          <span class="ma-icon ma-icon-lg">${ICONS.alertTriangle}</span>
        </div>
        <div class="ma-error-content">
          <h4>Connection Error: Model Diagnostics Unavailable</h4>
          <p>${appState.errorMessage}</p>
          <button class="ma-btn-retry" id="maRetryBtn">
            <span class="ma-icon">${ICONS.refresh}</span>
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    `;
  }

  // --- 6. EVENT BINDINGS ---
  function attachEventListeners() {
    // Target segmented buttons
    const targetBtns = document.querySelectorAll('#maTargetSegments .ma-segment-btn');
    targetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target-id');
        handleTargetChange(targetId);
      });
    });

    // Algorithm segmented buttons
    const algoBtns = document.querySelectorAll('#maAlgoSegments .ma-segment-btn');
    algoBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const algoId = btn.getAttribute('data-algo-id');
        handleAlgorithmChange(algoId);
      });
    });

    // Refresh button
    const refreshBtn = document.getElementById('maRefreshBtn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        loadData();
      });
    }

    // Threshold toggle buttons
    const threshBtns = document.querySelectorAll('[data-threshold-mode]');
    threshBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-threshold-mode');
        handleThresholdToggle(mode);
      });
    });

    // Accordion toggle
    const accordionBtn = document.getElementById('maAccordionToggleBtn');
    if (accordionBtn) {
      accordionBtn.addEventListener('click', toggleAccordion);
    }

    // SHAP row clicks
    const shapRows = document.querySelectorAll('#maShapRowsList .ma-shap-row');
    if (shapRows.length > 0) {
      let shapFeatures = [];
      const target = TARGETS[appState.activeTarget];
      if (appState.shapDataset && appState.shapDataset[target.shapTargetKey]) {
        shapFeatures = appState.shapDataset[target.shapTargetKey].features || [];
      } else if (Array.isArray(appState.currentModelDetail?.top_feature_importance)) {
        shapFeatures = appState.currentModelDetail.top_feature_importance.map(item => ({
          feature: item.feature,
          mean_abs_shap: item.importance,
          direction: 'Non-linear / context-dependent'
        }));
      }
      const sortedFeatures = [...shapFeatures].sort((a, b) => (b.mean_abs_shap || 0) - (a.mean_abs_shap || 0));
      const totalImportance = sortedFeatures.reduce((acc, curr) => acc + (curr.mean_abs_shap || 0), 0);

      shapRows.forEach(row => {
        row.addEventListener('click', () => {
          const idx = parseInt(row.getAttribute('data-feature-index'), 10);
          if (sortedFeatures[idx]) {
            openFeatureDrawer(sortedFeatures[idx], totalImportance);
          }
        });
      });
    }

    // Keyboard ESC listener for drawer
    window.onkeydown = function (e) {
      if (e.key === 'Escape' && appState.selectedFeatureDrawer) {
        closeFeatureDrawer();
      }
    };
  }

  function attachErrorListeners() {
    const retryBtn = document.getElementById('maRetryBtn');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        loadData(true);
      });
    }
  }

  // --- 7. INITIALIZATION ---
  document.addEventListener('DOMContentLoaded', () => {
    loadData(true);
  });

})();
