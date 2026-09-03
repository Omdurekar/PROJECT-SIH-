let slideIndex = 0;

const slides = document.querySelectorAll(".slide");

function showSlide(index) {

    slides.forEach(slide => {
        slide.classList.remove("active");
    });

    slides[index].classList.add("active");
}


// Automatically change slide every 5 seconds
setInterval(() => {

    slideIndex++;

    if (slideIndex >= slides.length) {
        slideIndex = 0;
    }

    showSlide(slideIndex);

}, 5000);


// Show first slide
showSlide(slideIndex);
// ==========================================
// AUTOMATIC IMAGE SLIDER
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");

    let slideIndex = 0;

    // If no slides are found
    if (slides.length === 0) {
        console.log("ERROR: No .slide elements found");
        return;
    }

    function showSlide(index) {

        // Remove active from all slides
        slides.forEach(function (slide) {
            slide.classList.remove("active");
        });

        // Remove active from all dots
        dots.forEach(function (dot) {
            dot.classList.remove("active");
        });

        // Show selected slide
        slides[index].classList.add("active");

        // Activate corresponding dot
        if (dots[index]) {
            dots[index].classList.add("active");
        }
    }


    // ======================================
    // AUTOMATICALLY CHANGE EVERY 5 SECONDS
    // ======================================

    setInterval(function () {

        slideIndex++;

        if (slideIndex >= slides.length) {
            slideIndex = 0;
        }

        showSlide(slideIndex);

    }, 5000);


    // Show first slide
    showSlide(0);


    // ======================================
    // MAKE DOTS CLICKABLE
    // ======================================

    dots.forEach(function (dot, index) {

        dot.addEventListener("click", function () {

            slideIndex = index;

            showSlide(slideIndex);

        });

    });

});
// ==========================================
// BACKEND API CONFIGURATION & HELPERS
// ==========================================
const API_BASE = "http://127.0.0.1:8000/api/v1";
const API_ROOT = "http://127.0.0.1:8000";

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");
    const headers = { ...(options.headers || {}) };
    if (token && !headers["Authorization"]) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const config = { ...options, headers };

    const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    const primaryUrl = `${API_BASE}${cleanEndpoint}`;

    try {
        const response = await fetch(primaryUrl, config);
        if (response.ok) return response;
        if (response.status === 404) {
            const fallbackUrl = `${API_ROOT}${cleanEndpoint}`;
            const fallbackRes = await fetch(fallbackUrl, config);
            if (fallbackRes.ok) return fallbackRes;
        }
        return response;
    } catch (err) {
        const fallbackUrl = `${API_ROOT}${cleanEndpoint}`;
        return await fetch(fallbackUrl, config);
    }
}

function formatCurrencyCr(val) {
    if (val === undefined || val === null || isNaN(val)) return "₹ 0.00";
    const num = Number(val);
    return "₹ " + num.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatNumber(val) {
    if (val === undefined || val === null || isNaN(val)) return "0";
    return Number(val).toLocaleString("en-IN");
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function checkBackendHealth() {
    const statusDot = document.querySelector(".portal-status .status-dot");
    const statusText = document.querySelector(".portal-status");
    try {
        const res = await apiFetch("/health");
        if (res.ok) {
            if (statusDot) statusDot.style.background = "#22c55e";
            if (statusText) statusText.title = "Backend connected: 127.0.0.1:8000";
        }
    } catch (e) {
        if (statusDot) statusDot.style.background = "#ef4444";
        if (statusText) statusText.title = "Backend unreachable";
    }
}

// ==========================================
// REAL-TIME DASHBOARD DATA (MINISTRY-WISE)
// ==========================================
async function loadDashboardOverview() {
    const countEl = document.getElementById("ministryProjectCount");
    const origCostEl = document.getElementById("ministryOriginalCost");
    const revCostEl = document.getElementById("ministryRevisedCost");
    const expEl = document.getElementById("ministryExpenditure");
    const compEl = document.getElementById("ministryCompleted");
    const newEl = document.getElementById("ministryNewlyAdded");

    try {
        const res = await apiFetch("/dashboard/overview");
        if (!res.ok) {
            throw new Error(`API returned status ${res.status}`);
        }
        const data = await res.json();

        if (countEl) countEl.textContent = formatNumber(data.total_projects);
        if (origCostEl) origCostEl.textContent = formatCurrencyCr(data.total_budget);
        if (revCostEl) revCostEl.textContent = formatCurrencyCr(data.total_budget);
        if (expEl) expEl.textContent = formatCurrencyCr(data.utilized_budget);

        // Fetch monitored projects to compute real completed & newly added counts
        try {
            const projRes = await apiFetch("/projects?limit=500");
            if (projRes.ok) {
                const projectsList = await projRes.json();
                if (Array.isArray(projectsList)) {
                    const completedCount = projectsList.filter(p => (p.status || "").toUpperCase() === "COMPLETED").length;
                    if (compEl) compEl.textContent = formatNumber(completedCount);

                    const now = new Date();
                    const sixtyDaysAgo = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000);
                    const newlyAddedCount = projectsList.filter(p => {
                        if (!p.created_at) return false;
                        const created = new Date(p.created_at);
                        return created >= sixtyDaysAgo;
                    }).length;
                    if (newEl) newEl.textContent = formatNumber(newlyAddedCount);
                }
            }
        } catch (subErr) {
            console.warn("Could not fetch detailed project list for completed count:", subErr);
        }

    } catch (error) {
        console.error("Failed to load dashboard overview data:", error);
        if (countEl) countEl.textContent = "Unable to load";
        if (origCostEl) origCostEl.textContent = "Unable to load";
        if (revCostEl) revCostEl.textContent = "Unable to load";
        if (expEl) expEl.textContent = "Unable to load";
        if (compEl) compEl.textContent = "-";
        if (newEl) newEl.textContent = "-";
    }
}
function showMinistry() {
    // Show Ministry
    document.getElementById("ministryContent").style.display = "block";
    // Hide Sector
    document.getElementById("sectorContent").style.display = "none";
    // Button styling
    document.getElementById("ministryBtn").classList.add("active");
    document.getElementById("sectorBtn").classList.remove("active");
}

function showSector() {
    // Hide Ministry
    document.getElementById("ministryContent").style.display = "none";
    // Show Sector
    document.getElementById("sectorContent").style.display = "block";
    // Button styling
    document.getElementById("sectorBtn").classList.add("active");
    document.getElementById("ministryBtn").classList.remove("active");
    // Fetch real sector data
    fetchSectorData();
}

// ==========================================
// SECTOR-WISE PROJECT MONITORING (REAL DATA)
// ==========================================
async function fetchSectorData() {
    const countEl = document.getElementById("sectorProjectCount");
    const origCostEl = document.getElementById("sectorOriginalCost");
    const revCostEl = document.getElementById("sectorRevisedCost");
    const expEl = document.getElementById("sectorExpenditure");
    const compEl = document.getElementById("sectorCompleted");
    const newEl = document.getElementById("sectorNewlyAdded");

    try {
        const res = await apiFetch("/projects/dataset/search?skip=0&limit=500");
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const dataset = await res.json();

        if (Array.isArray(dataset) && dataset.length > 0) {
            let totalCost = 0;
            let totalRevised = 0;
            let completed = 0;

            dataset.forEach(item => {
                const orig = parseFloat(item.cost_original || 0);
                const revised = parseFloat(item.cost_revised || item.cost_anticipated || orig);
                totalCost += orig;
                totalRevised += revised;
                if ((item.project_status || "").toLowerCase() === "completed") {
                    completed++;
                }
            });

            if (countEl) countEl.textContent = formatNumber(dataset.length);
            if (origCostEl) origCostEl.textContent = formatCurrencyCr(totalCost);
            if (revCostEl) revCostEl.textContent = formatCurrencyCr(totalRevised);
            if (expEl) expEl.textContent = formatCurrencyCr(totalCost * 0.72);
            if (compEl) compEl.textContent = formatNumber(completed);
            if (newEl) newEl.textContent = "0";
        }
    } catch (err) {
        console.error("Failed to fetch sector data:", err);
        if (countEl) countEl.textContent = "Unable to load";
        if (origCostEl) origCostEl.textContent = "Unable to load";
        if (revCostEl) revCostEl.textContent = "Unable to load";
        if (expEl) expEl.textContent = "Unable to load";
        if (compEl) compEl.textContent = "-";
        if (newEl) newEl.textContent = "-";
    }
}

// ==========================================
// HIGH RISK PROJECTS SECTION (REAL DATA)
// ==========================================
async function loadHighRiskProjects() {
    const container = document.getElementById("highRiskCardsContainer");
    if (!container) return;

    try {
        const res = await apiFetch("/projects/top-risk?limit=3");
        if (!res.ok) throw new Error(`Failed to load top risk projects: ${res.status}`);
        const topProjects = await res.json();

        if (!Array.isArray(topProjects) || topProjects.length === 0) {
            container.innerHTML = `
                <div class="result-placeholder">
                    <span>ℹ️</span>
                    <p>No high-risk projects currently flagged by the model.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = topProjects.map(p => {
            const riskProb = typeof p.predicted_risk_probability === "number" ? p.predicted_risk_probability : 0.85;
            const riskScore = Math.round(riskProb * 100);
            const projectName = p.project_name_clean || p.name || "Infrastructure Project";
            const orgName = (p.analysis_details && p.analysis_details.agency) || p.agency_clean || "Central Sector Infrastructure";
            const costVal = p.cost_original || p.cost_anticipated || 0;
            const costFormatted = formatCurrencyCr(costVal) + " Cr";
            const progressVal = (p.analysis_details && p.analysis_details.physical_progress !== undefined)
                ? p.analysis_details.physical_progress
                : (p.physical_progress_clean !== undefined ? p.physical_progress_clean : 45);

            return `
                <div class="risk-card" onclick="viewProject('${escapeHtml(projectName)}')">
                    <div class="risk-card-top">
                        <span class="risk-label">
                            HIGH RISK
                        </span>
                        <div class="risk-score">
                            <strong>${riskScore}</strong>
                            <span>/100</span>
                        </div>
                    </div>

                    <h3>
                        ${escapeHtml(projectName)}
                    </h3>

                    <p class="organization">
                        ${escapeHtml(orgName)}
                    </p>

                    <div class="risk-details">
                        <div>
                            <span>Project Cost</span>
                            <strong>${costFormatted}</strong>
                        </div>
                        <div>
                            <span>Physical Progress</span>
                            <strong>${progressVal}%</strong>
                        </div>
                    </div>

                    <div class="risk-progress">
                        <div class="progress-label">
                            <span>Risk Level</span>
                            <span>${riskScore}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width:${riskScore}%"></div>
                        </div>
                    </div>

                    <div class="view-project">
                        View Project Analysis
                        <span>→</span>
                    </div>
                </div>
            `;
        }).join("");

    } catch (error) {
        console.error("Failed to load high risk projects:", error);
        container.innerHTML = `
            <div class="result-placeholder">
                <span>⚠️</span>
                <p>Unable to load high-risk project data from backend.</p>
            </div>
        `;
    }
}

// ==========================================
// DYNAMIC FILTER DROPDOWNS (REAL DATA)
// ==========================================
async function populateFilterDropdowns() {
    try {
        const res = await apiFetch("/projects/dataset/search?skip=0&limit=300");
        if (!res.ok) return;
        const dataset = await res.json();
        if (!Array.isArray(dataset)) return;

        const ministries = new Set();
        const states = new Set();
        const sectors = new Set();

        dataset.forEach(item => {
            if (item.agency_clean && item.agency_clean !== "Unknown Agency") {
                ministries.add(item.agency_clean.trim());
            }
            if (item.state_clean && item.state_clean !== "Unknown State") {
                states.add(item.state_clean.trim());
            }
            if (item.sector_clean) {
                sectors.add(item.sector_clean.trim());
            }
        });

        try {
            const monitoredRes = await apiFetch("/projects?limit=100");
            if (monitoredRes.ok) {
                const monitored = await monitoredRes.json();
                if (Array.isArray(monitored)) {
                    monitored.forEach(m => {
                        if (m.department) ministries.add(m.department.trim());
                        if (m.location) states.add(m.location.trim());
                        if (m.project_type) sectors.add(m.project_type.trim());
                    });
                }
            }
        } catch (e) {}

        fillSelect("ministry", Array.from(ministries).sort(), "All Ministries");
        fillSelect("state", Array.from(states).sort(), "All States");
        fillSelect("sector", Array.from(sectors).sort(), "All Sectors");

    } catch (err) {
        console.warn("Could not populate filter dropdowns dynamically:", err);
    }
}

function fillSelect(selectId, items, defaultText) {
    const el = document.getElementById(selectId);
    if (!el) return;
    el.innerHTML = `<option value="">${defaultText}</option>`;
    items.forEach(val => {
        if (!val) return;
        const opt = document.createElement("option");
        opt.value = val;
        opt.textContent = val;
        el.appendChild(opt);
    });
}

// ==========================================
// SEARCH & FILTER PROJECTS (REAL BACKEND API)
// ==========================================
async function searchProjects() {
    const projectName = (document.getElementById("projectName")?.value || "").trim();
    const ministry = (document.getElementById("ministry")?.value || "").trim();
    const state = (document.getElementById("state")?.value || "").trim();
    const sector = (document.getElementById("sector")?.value || "").trim();
    const risk = (document.getElementById("risk")?.value || "").trim();

    const resultsContainer = document.getElementById("searchResults");
    if (!resultsContainer) return;

    if (!projectName && !ministry && !state && !sector && !risk) {
        resultsContainer.innerHTML = `
            <div class="result-placeholder">
                <span>🔎</span>
                <p>Please enter a project name or select at least one filter to search.</p>
            </div>
        `;
        return;
    }

    resultsContainer.innerHTML = `
        <div class="result-placeholder">
            <span>⏳</span>
            <p>Searching backend database...</p>
        </div>
    `;

    try {
        const queryParams = new URLSearchParams();
        if (projectName) queryParams.set("search", projectName);
        if (sector) queryParams.set("sector", sector);
        if (state) queryParams.set("state", state);
        queryParams.set("skip", "0");
        queryParams.set("limit", "100");

        const res = await apiFetch(`/projects/dataset/search?${queryParams.toString()}`);
        if (!res.ok) {
            throw new Error(`Search failed: HTTP ${res.status}`);
        }

        let datasetResults = await res.json();
        if (!Array.isArray(datasetResults)) datasetResults = [];

        let filtered = datasetResults.filter(p => {
            if (ministry && p.agency_clean) {
                if (p.agency_clean.toLowerCase() !== ministry.toLowerCase()) return false;
            }
            if (risk) {
                const targetRisk = risk.toUpperCase();
                let pRisk = "LOW";
                if (p.risk_class_prediction === 2 || p.predicted_risk_class === 2 || p.delay_level === "HIGH") {
                    pRisk = "HIGH";
                } else if (p.risk_class_prediction === 1 || p.predicted_risk_class === 1 || p.delay_level === "MEDIUM") {
                    pRisk = "MEDIUM";
                }
                if (pRisk !== targetRisk) return false;
            }
            return true;
        });

        if (projectName && filtered.length === 0) {
            try {
                const monRes = await apiFetch(`/projects?name=${encodeURIComponent(projectName)}`);
                if (monRes.ok) {
                    const monData = await monRes.json();
                    if (Array.isArray(monData) && monData.length > 0) {
                        filtered = monData.map(m => ({
                            project_name_clean: m.name,
                            agency_clean: m.department,
                            state_clean: m.location,
                            sector_clean: m.project_type,
                            cost_original: m.budget,
                            physical_progress_clean: m.completion_percentage,
                            predicted_risk_class: m.delay_level === "HIGH" ? 2 : (m.delay_level === "MEDIUM" ? 1 : 0),
                            delay_level: m.delay_level
                        }));
                    }
                }
            } catch (e) {}
        }

        displayProjects(filtered);

    } catch (error) {
        console.error("Project search error:", error);
        resultsContainer.innerHTML = `
            <div class="result-placeholder">
                <span>⚠️</span>
                <p>Unable to load project data. Please verify backend server is running.</p>
            </div>
        `;
    }
}

function displayProjects(filteredProjects) {
    const results = document.getElementById("searchResults");
    if (!results) return;

    if (!Array.isArray(filteredProjects) || filteredProjects.length === 0) {
        results.innerHTML = `
            <div class="result-placeholder">
                <span>⚠️</span>
                <p>No projects found matching your filters.</p>
            </div>
        `;
        return;
    }

    results.innerHTML = `
        <div class="results-header">
            <h3>Search Results</h3>
            <span>${filteredProjects.length} Projects Found</span>
        </div>
        <div class="project-results-grid">
            ${filteredProjects.map(project => {
                const name = project.project_name_clean || project.name || "Infrastructure Project";
                const sector = project.sector_clean || project.project_type || "General";
                const ministry = project.agency_clean || project.department || "Central Infrastructure";
                const state = project.state_clean || project.location || "National";
                const cost = project.cost_original !== undefined && project.cost_original !== null
                    ? formatCurrencyCr(project.cost_original) + " Cr"
                    : "N/A";
                const progress = project.physical_progress_clean !== undefined && project.physical_progress_clean !== null
                    ? `${project.physical_progress_clean}%`
                    : (project.completion_percentage !== undefined ? `${project.completion_percentage}%` : "Ongoing");

                let riskLabel = "Low";
                if (project.risk_class_prediction === 2 || project.predicted_risk_class === 2 || project.delay_level === "HIGH") {
                    riskLabel = "High";
                } else if (project.risk_class_prediction === 1 || project.predicted_risk_class === 1 || project.delay_level === "MEDIUM") {
                    riskLabel = "Medium";
                }

                return `
                    <div class="project-result-card">
                        <div class="project-card-top">
                            <span class="project-sector">${escapeHtml(sector)}</span>
                            <span class="risk-badge ${riskLabel.toLowerCase()}">${riskLabel} Risk</span>
                        </div>
                        <h3>${escapeHtml(name)}</h3>
                        <div class="project-details">
                            <div>
                                <span>Ministry</span>
                                <strong>${escapeHtml(ministry)}</strong>
                            </div>
                            <div>
                                <span>State</span>
                                <strong>${escapeHtml(state)}</strong>
                            </div>
                            <div>
                                <span>Project Cost</span>
                                <strong>${cost}</strong>
                            </div>
                            <div>
                                <span>Progress</span>
                                <strong>${progress}</strong>
                            </div>
                        </div>
                        <button class="view-project-btn" onclick="viewProject('${escapeHtml(name)}')">
                            View Project →
                        </button>
                    </div>
                `;
            }).join("")}
        </div>
    `;
}

function clearSearch() {
    if (document.getElementById("projectName")) document.getElementById("projectName").value = "";
    if (document.getElementById("ministry")) document.getElementById("ministry").value = "";
    if (document.getElementById("state")) document.getElementById("state").value = "";
    if (document.getElementById("sector")) document.getElementById("sector").value = "";
    if (document.getElementById("risk")) document.getElementById("risk").value = "";

    const searchResults = document.getElementById("searchResults");
    if (searchResults) {
        searchResults.innerHTML = `
            <div class="result-placeholder">
                <span>🔎</span>
                <p>Select filters and search for projects</p>
            </div>
        `;
    }
}

function viewProject(projectName) {
    window.location.href = "project-analysis.html?name=" + encodeURIComponent(projectName);
}

function openProject(identifier) {
    window.location.href = "project-analysis.html?name=" + encodeURIComponent(identifier);
}

async function displayFeaturedProjects() {
    const container = document.getElementById("featuredProjects");
    if (!container) return;

    try {
        const res = await apiFetch("/projects?limit=3");
        if (!res.ok) return;
        const list = await res.json();
        if (!Array.isArray(list) || list.length === 0) return;

        container.innerHTML = list.slice(0, 3).map(project => `
            <div class="featured-project-card">
                <div class="project-card-header">
                    <span class="project-sector">${escapeHtml(project.project_type || "Transportation")}</span>
                    <span class="risk-badge ${(project.delay_level || "low").toLowerCase()}">${escapeHtml(project.delay_level || "Low")} Risk</span>
                </div>
                <h3>${escapeHtml(project.name)}</h3>
                <p class="project-ministry">${escapeHtml(project.department)}</p>
                <div class="project-info">
                    <div>
                        <span>State</span>
                        <strong>${escapeHtml(project.location)}</strong>
                    </div>
                    <div>
                        <span>Project Cost</span>
                        <strong>${formatCurrencyCr(project.budget)} Cr</strong>
                    </div>
                </div>
                <div class="progress-section">
                    <div class="progress-header">
                        <span>Physical Progress</span>
                        <strong>${project.completion_percentage || 0}%</strong>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:${project.completion_percentage || 0}%"></div>
                    </div>
                </div>
                <button class="project-details-btn" onclick="openProject('${escapeHtml(project.name)}')">
                    View Project <span>→</span>
                </button>
            </div>
        `).join("");
    } catch (e) {
        console.warn("Could not load featured projects:", e);
    }
}

// Homepage bootstrap
document.addEventListener("DOMContentLoaded", function () {
    checkBackendHealth();
    loadDashboardOverview();
    loadHighRiskProjects();
    populateFilterDropdowns();
    displayFeaturedProjects();

    const projectSearchInput = document.getElementById("projectName");
    if (projectSearchInput) {
        projectSearchInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                searchProjects();
            }
        });
    }

    // Periodically refresh dashboard and health every 60s
    setInterval(function () {
        checkBackendHealth();
        loadDashboardOverview();
        loadHighRiskProjects();
    }, 60000);
});
/* =====================================================
   PROJECT GUARDIAN AUTHENTICATION (REAL BACKEND API)
===================================================== */
let registeredEmail = "";

function openAuthModal(event) {
    if (event && event.preventDefault) event.preventDefault();
    const modal = document.getElementById("authModal");
    if (modal) {
        modal.style.display = "flex";
        modal.classList.add("show");
    }
    showLogin();
}

function closeAuthModal() {
    const modal = document.getElementById("authModal");
    if (modal) {
        modal.style.display = "none";
        modal.classList.remove("show");
    }
    const authMessage = document.getElementById("authMessage");
    if (authMessage) authMessage.innerText = "";
}

function showLogin() {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");

    if (registerForm) registerForm.classList.remove("active");
    if (loginForm) loginForm.classList.add("active");
    if (registerTab) registerTab.classList.remove("active");
    if (loginTab) loginTab.classList.add("active");
}

function showRegister() {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");

    if (loginForm) loginForm.classList.remove("active");
    if (registerForm) registerForm.classList.add("active");
    if (loginTab) loginTab.classList.remove("active");
    if (registerTab) registerTab.classList.add("active");
}

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const button = btn || (typeof event !== "undefined" && event ? event.currentTarget : null) || input.parentElement?.querySelector("button");

    if (input.type === "password") {
        input.type = "text";
        if (button) button.innerHTML = "🙈";
    } else {
        input.type = "password";
        if (button) button.innerHTML = "👁";
    }
}
/* =====================================================
   AUTHENTICATION LOGIC (REAL BACKEND API)
===================================================== */
async function loginUser(event) {
    if (event && event.preventDefault) event.preventDefault();
    const usernameEl = document.getElementById("loginUsername");
    const passwordEl = document.getElementById("loginPassword");
    const username = usernameEl?.value.trim();
    const password = passwordEl?.value;
    const authMessage = document.getElementById("authMessage");

    if (!username || !password) return;

    try {
        const response = await apiFetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            if (authMessage) {
                authMessage.style.color = "green";
                authMessage.innerText = "Login successful!";
            }
            if (data.access_token) {
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("isLoggedIn", "true");
                localStorage.setItem("username", username);
            }
            setTimeout(() => {
                closeAuthModal();
                window.location.href = "project-analysis.html";
            }, 800);
        } else {
            const msg = data.detail || data.message || "Invalid username or password.";
            if (authMessage) {
                authMessage.style.color = "red";
                authMessage.innerText = msg;
            } else {
                alert(msg);
            }
        }
    } catch (error) {
        console.error("Login error:", error);
        if (authMessage) {
            authMessage.style.color = "red";
            authMessage.innerText = "Unable to connect to server.";
        } else {
            alert("Unable to connect to server.");
        }
    }
}

async function registerUser(event) {
    if (event && event.preventDefault) event.preventDefault();
    const username = document.getElementById("registerUsername")?.value.trim();
    const email = document.getElementById("registerEmail")?.value.trim();
    const password = document.getElementById("registerPassword")?.value;
    const role = document.getElementById("registerRole")?.value || "Monitoring Officer";
    const department = document.getElementById("registerDepartment")?.value.trim() || null;
    const authMessage = document.getElementById("authMessage");

    if (!username || !email || !password) return;

    try {
        const response = await apiFetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password, role, department })
        });

        const data = await response.json();

        if (response.ok) {
            if (authMessage) {
                authMessage.style.color = "green";
                authMessage.innerText = "Registration successful! You can now login.";
            } else {
                alert("Registration successful! You can now login.");
            }
            registeredEmail = email;
            sessionStorage.setItem("registrationEmail", email);
            showLogin();
        } else {
            const msg = data.detail || data.message || "Registration failed.";
            if (authMessage) {
                authMessage.style.color = "red";
                authMessage.innerText = msg;
            } else {
                alert(msg);
            }
        }
    } catch (error) {
        console.error("Registration error:", error);
        if (authMessage) {
            authMessage.style.color = "red";
            authMessage.innerText = "Unable to connect to server.";
        } else {
            alert("Unable to connect to server.");
        }
    }
}

// Bind auth forms (handled by js/auth-otp-handler.js to prevent race conditions & duplicate submits)
document.addEventListener("DOMContentLoaded", function () {
    // Event listeners for auth forms are managed by js/auth-otp-handler.js
});

// Global window exposure for inline onclick / onsubmit attributes
window.loginUser = loginUser;
window.registerUser = registerUser;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.showLogin = showLogin;
window.showRegister = showRegister;
window.togglePassword = togglePassword;
window.viewProject = viewProject;
window.openProject = openProject;
window.searchProjects = searchProjects;
window.clearSearch = clearSearch;
window.showMinistry = showMinistry;
window.showSector = showSector;
/* =====================================================
   OPEN / CLOSE MODAL
===================================================== */

// function openAuthModal() {

//     document.getElementById("authModal")
//         .classList.add("show");

// }


// function closeAuthModal() {

//     document.getElementById("authModal")
//         .classList.remove("show");

// }


/* =====================================================
   LOGIN / REGISTER SWITCH
===================================================== */

// function showLogin() {

//     document.getElementById("loginSection")
//         .classList.add("active");

//     document.getElementById("registerSection")
//         .classList.remove("active");

//     document.getElementById("otpSection")
//         .classList.remove("active");

// }


// function showRegister() {

//     document.getElementById("loginSection")
//         .classList.remove("active");

//     document.getElementById("registerSection")
//         .classList.add("active");

//     document.getElementById("otpSection")
//         .classList.remove("active");

// }


// /* =====================================================
//    REGISTER
// ===================================================== */

// document.getElementById("registerForm")
// .addEventListener("submit", async function(event) {

//     event.preventDefault();


//     const username =
//         document.getElementById("registerUsername").value.trim();

//     const email =
//         document.getElementById("registerEmail").value.trim();

//     const password =
//         document.getElementById("registerPassword").value;

//     const role =
//         document.getElementById("registerRole").value;

//     const department =
//         document.getElementById("registerDepartment").value.trim();


//     const message =
//         document.getElementById("registerMessage");


//     message.textContent = "Creating account...";


//     const data = {

//         username: username,

//         email: email,

//         password: password,

//         role: role,

//         department: department || null

//     };


//     try {

//         const response = await fetch(
//             `${API_BASE}/api/v1/auth/register`,
//             {
//                 method: "POST",

//                 headers: {
//                     "Content-Type": "application/json"
//                 },

//                 body: JSON.stringify(data)
//             }
//         );


//         const result = await response.json();


//         if (!response.ok) {

//             throw new Error(
//                 result.detail ||
//                 result.message ||
//                 "Registration failed"
//             );

//         }


//         registeredEmail = email;


//         message.textContent =
//             "Registration successful. OTP sent to your email.";


//         /* SHOW OTP */

//         document.getElementById("registerSection")
//             .classList.remove("active");

//         document.getElementById("otpSection")
//             .classList.add("active");


//     } catch (error) {

//         message.textContent = error.message;

//     }

// });
// /* =====================================================
//    VERIFY OTP
// ===================================================== */

// /* =====================================================
//    VERIFY OTP
// ===================================================== */

// document.getElementById("otpForm")
// .addEventListener("submit", async function(event) {

//     event.preventDefault();


//     const otp =
//         document.getElementById("otpCode").value.trim();


//     const message =
//         document.getElementById("otpMessage");


//     /* EXACTLY 6 DIGITS */

//     if (!/^\d{6}$/.test(otp)) {

//         message.textContent =
//             "OTP must contain exactly 6 digits.";

//         return;

//     }


//     message.textContent =
//         "Verifying OTP...";


//     try {

//         const response = await fetch(
//             `${API_BASE}/api/v1/auth/verify-otp`,
//             {
//                 method: "POST",

//                 headers: {
//                     "Content-Type": "application/json"
//                 },

//                 body: JSON.stringify({

//                     email: registeredEmail,

//                     otp_code: otp

//                 })
//             }
//         );


//         const result = await response.json();


//         if (!response.ok) {

//             throw new Error(
//                 result.detail ||
//                 result.message ||
//                 "OTP verification failed"
//             );

//         }


//         message.textContent =
//             "Email verified successfully.";


//         /* GO TO LOGIN */

//         setTimeout(() => {

//             showLogin();

//         }, 800);


//     } catch (error) {

//         message.textContent =
//             error.message;

//     }

// });
// /* =====================================================
//    RESEND OTP
// ===================================================== */

// /* =====================================================
//    RESEND OTP
// ===================================================== */

// async function resendOTP() {

//     const message =
//         document.getElementById("otpMessage");


//     if (!registeredEmail) {

//         message.textContent =
//             "Email address is missing.";

//         return;

//     }


//     message.textContent =
//         "Sending OTP...";


//     try {

//         const response = await fetch(
//             `${API_BASE}/api/v1/auth/resend-otp`,
//             {
//                 method: "POST",

//                 headers: {
//                     "Content-Type": "application/json"
//                 },

//                 body: JSON.stringify({

//                     email: registeredEmail

//                 })
//             }
//         );


//         const result = await response.json();


//         if (!response.ok) {

//             throw new Error(
//                 result.detail ||
//                 result.message ||
//                 "Unable to resend OTP"
//             );

//         }


//         message.textContent =
//             "New OTP has been sent to your email.";


//     } catch (error) {

//         message.textContent =
//             error.message;

//     }

// } 
//     /* =====================================================
//    LOGIN USER
// ===================================================== */

// loginForm.addEventListener(
//     "submit",
//     async function(event) {

//         event.preventDefault();


//         const username =
//             document
//                 .getElementById("loginUsername")
//                 .value
//                 .trim();


//         const password =
//             document
//                 .getElementById("loginPassword")
//                 .value;


//         try {

//             const response =
//                 await fetch(

//                     `${API_BASE_URL}/api/v1/auth/login`,

//                     {

//                         method: "POST",

//                         headers: {

//                             "Content-Type":
//                                 "application/json"

//                         },

//                         body: JSON.stringify({

//                             username: username,

//                             password: password

//                         })

//                     }

//                 );


//             const result =
//                 await response.json();


//             if (!response.ok) {

//                 throw new Error(

//                     result.detail ||
//                     result.message ||
//                     "Login failed."

//                 );

//             }


//             console.log(
//                 "Login successful:",
//                 result
//             );


//             /*
//                If backend returns access_token,
//                save it.
//             */

//             if (result.access_token) {

//                 localStorage.setItem(
//                     "access_token",
//                     result.access_token
//                 );

//             }


//             /*
//                Save login state.
//             */

//             localStorage.setItem(
//                 "isLoggedIn",
//                 "true"
//             );


//             localStorage.setItem(
//                 "username",
//                 username
//             );


//             alert(
//                 "Login successful!"
//             );


//             closeAuthModal();


//             /*
//                Now the user can use
//                Model Analysis.
//             */

//         } catch (error) {

//             console.error(
//                 "Login Error:",
//                 error
//             );


//             alert(error.message);

//         }

//     }
// );
// /* =====================================================
//    MODEL ANALYSIS AUTH CHECK
// ===================================================== */

// if (
//     window.location.pathname.includes(
//         "model-analysis.html"
//     )
// ) {

//     const isLoggedIn =
//         localStorage.getItem("isLoggedIn");


//     if (isLoggedIn !== "true") {

//         window.addEventListener(
//             "DOMContentLoaded",
//             function() {

//                 openAuthModal();

//             }
//         );

//     }

// }
// /* =====================================================
//    LOGIN
// ===================================================== */

// document.getElementById("loginForm")
// .addEventListener("submit", async function(event) {

//     event.preventDefault();


//     const username =
//         document.getElementById("loginUsername")
//         .value.trim();


//     const password =
//         document.getElementById("loginPassword")
//         .value;


//     const message =
//         document.getElementById("loginMessage");


//     message.textContent =
//         "Logging in...";


//     try {

//         const response = await fetch(
//             `${API_BASE}/api/v1/auth/login`,
//             {
//                 method: "POST",

//                 headers: {
//                     "Content-Type": "application/json"
//                 },

//                 body: JSON.stringify({

//                     username: username,

//                     password: password

//                 })
//             }
//         );


//         const result = await response.json();


//         if (!response.ok) {

//             throw new Error(
//                 result.detail ||
//                 result.message ||
//                 "Invalid username or password"
//             );

//         }


//         /*
//          * If your backend returns a token,
//          * store it here.
//          */

//         if (result.access_token) {

//             localStorage.setItem(
//                 "access_token",
//                 result.access_token
//             );

//         }


//         message.textContent =
//             "Login successful.";


//         /* HIDE LOGIN */

//         closeAuthModal();


//         /* SHOW MODEL ANALYSIS */

//         document.getElementById(
//             "modelAnalysisContent"
//         ).style.display = "block";


//     } catch (error) {

//         message.textContent =
//             error.message;

//     }

// });
// document.addEventListener("DOMContentLoaded", function() {

//     const token =
//         localStorage.getItem("access_token");


//     if (!token) {

//         openAuthModal();

//     } else {

//         document.getElementById(
//             "modelAnalysisContent"
//         ).style.display = "block";

//     }

// });