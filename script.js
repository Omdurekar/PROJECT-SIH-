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
async function searchProjects() {

    const projectName =
        document.getElementById("projectName").value;

    const ministry =
        document.getElementById("ministry").value;

    const state =
        document.getElementById("state").value;

    const sector =
        document.getElementById("sector").value;

    const risk =
        document.getElementById("risk").value;

    const projectSize =
        document.getElementById("projectSize").value;

    const progress =
        document.getElementById("progress").value;

    const overrun =
        document.getElementById("overrun").value;


    const filters = {

        project_name: projectName,

        ministry: ministry,

        state: state,

        sector: sector,

        risk_category: risk,

        project_size: projectSize,

        physical_progress: progress,

        time_overrun: overrun

    };


    console.log("Sending filters:", filters);


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/projects/search",
            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(filters)

            }
        );


        if (!response.ok) {

            throw new Error("Unable to fetch projects");

        }


        const data = await response.json();


        displaySearchResults(data);


    } catch (error) {

        console.error(error);

        document.getElementById("searchResults").innerHTML = `

            <div class="result-placeholder">

                <span>⚠️</span>

                <p>
                    Backend is not connected.
                    Please check the FastAPI server.
                </p>

            </div>

        `;

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


    // Fetch sector data
    fetchSectorData();
}
const projects = [
    {
        name: "Mumbai-Ahmedabad High Speed Rail",
        ministry: "Ministry of Railways",
        state: "Maharashtra",
        sector: "Transport",
        risk: "High",
        cost: "₹1,08,000 Cr",
        progress: "65%"
    },

    {
        name: "Delhi-Mumbai Expressway",
        ministry: "Ministry of Road Transport",
        state: "Maharashtra",
        sector: "Road Transport",
        risk: "Medium",
        cost: "₹98,000 Cr",
        progress: "82%"
    },

    {
        name: "National River Linking Project",
        ministry: "Ministry of Jal Shakti",
        state: "Madhya Pradesh",
        sector: "Water Resources",
        risk: "High",
        cost: "₹60,000 Cr",
        progress: "42%"
    },

    {
        name: "AIIMS Infrastructure Development",
        ministry: "Ministry of Health",
        state: "Delhi",
        sector: "Health",
        risk: "Low",
        cost: "₹15,000 Cr",
        progress: "90%"
    },

    {
        name: "Dedicated Freight Corridor",
        ministry: "Ministry of Railways",
        state: "Uttar Pradesh",
        sector: "Transport",
        risk: "Medium",
        cost: "₹81,459 Cr",
        progress: "74%"
    },

    {
        name: "Mumbai Metro Rail Project",
        ministry: "Ministry of Housing",
        state: "Maharashtra",
        sector: "Urban Development",
        risk: "High",
        cost: "₹45,000 Cr",
        progress: "55%"
    }
];
document.addEventListener("DOMContentLoaded", function () {

    populateDropdown(
        "ministry",
        "ministry",
        "All Ministries"
    );

    populateDropdown(
        "state",
        "state",
        "All States"
    );

    populateDropdown(
        "sector",
        "sector",
        "All Sectors"
    );

});
function populateDropdown(id, property, defaultText) {

    const select = document.getElementById(id);

    const values = [
        ...new Set(
            projects.map(project => project[property])
        )
    ];

    values.forEach(value => {

        const option = document.createElement("option");

        option.value = value;

        option.textContent = value;

        select.appendChild(option);

    });
}
function searchProjects() {

    // Get values from search fields
    const projectName = document
        .getElementById("projectName")
        .value
        .trim()
        .toLowerCase();

    const ministry = document.getElementById("ministry").value;
    const state = document.getElementById("state").value;
    const sector = document.getElementById("sector").value;
    const risk = document.getElementById("risk").value;

    // Result container
    const results = document.getElementById("searchResults");


    // ==========================================
    // CHECK IF USER GAVE ANY CONSTRAINT
    // ==========================================

    if (
        projectName === "" &&
        ministry === "" &&
        state === "" &&
        sector === "" &&
        risk === ""
    ) {

        results.innerHTML = `
            <div class="result-placeholder">
                <span>🔎</span>

                <p>
                    Please enter a project name or select
                    at least one filter to search.
                </p>
            </div>
        `;

        return;
    }


    // ==========================================
    // FILTER PROJECTS
    // ==========================================

    const filteredProjects = projects.filter(project => {

        // Project name typing search
        const nameMatch =
            project.name.toLowerCase().includes(projectName);


        // Ministry
        const ministryMatch =
            ministry === "" ||
            project.ministry === ministry;


        // State
        const stateMatch =
            state === "" ||
            project.state === state;


        // Sector
        const sectorMatch =
            sector === "" ||
            project.sector === sector;


        // Risk
        const riskMatch =
            risk === "" ||
            project.risk === risk;


        // ALL selected conditions must match
        return (
            nameMatch &&
            ministryMatch &&
            stateMatch &&
            sectorMatch &&
            riskMatch
        );

    });


    // ==========================================
    // DISPLAY RESULTS
    // ==========================================

    displayProjects(filteredProjects);
}
function displayProjects(filteredProjects) {

    const results =
        document.getElementById("searchResults");


    if (filteredProjects.length === 0) {

        results.innerHTML = `
            <div class="result-placeholder">

                <span>⚠️</span>

                <p>
                    No projects found matching your filters.
                </p>

            </div>
        `;

        return;
    }


    results.innerHTML = `

        <div class="results-header">

            <h3>
                Search Results
            </h3>

            <span>
                ${filteredProjects.length} Projects Found
            </span>

        </div>

        <div class="project-results-grid">

            ${filteredProjects.map(project => `

                <div class="project-result-card">

                    <div class="project-card-top">

                        <span class="project-sector">
                            ${project.sector}
                        </span>

                        <span class="risk-badge ${project.risk.toLowerCase()}">
                            ${project.risk} Risk
                        </span>

                    </div>


                    <h3>
                        ${project.name}
                    </h3>


                    <div class="project-details">

                        <div>
                            <span>Ministry</span>
                            <strong>
                                ${project.ministry}
                            </strong>
                        </div>

                        <div>
                            <span>State</span>
                            <strong>
                                ${project.state}
                            </strong>
                        </div>

                        <div>
                            <span>Project Cost</span>
                            <strong>
                                ${project.cost}
                            </strong>
                        </div>

                        <div>
                            <span>Progress</span>
                            <strong>
                                ${project.progress}
                            </strong>
                        </div>

                    </div>


                    <button
                        class="view-project-btn"
                        onclick="viewProject('${project.name}')">

                        View Project →

                    </button>

                </div>

            `).join("")}

        </div>
    `;
}
function clearSearch() {

    document.getElementById("projectName").value = "";

    document.getElementById("ministry").value = "";

    document.getElementById("state").value = "";

    document.getElementById("sector").value = "";

    document.getElementById("risk").value = "";


    document.getElementById("searchResults").innerHTML = `

        <div class="result-placeholder">

            <span>🔎</span>

            <p>
                Select filters and search for projects
            </p>

        </div>

    `;
}
function viewProject(projectName) {

    console.log("Opening:", projectName);

    // Later you can redirect to:
    // project-details.html?name=...

    window.location.href =
        "project-details.html?name=" +
        encodeURIComponent(projectName);
}
const featuredProjects = [

    {
        id: 1,
        name: "Mumbai-Ahmedabad High Speed Rail",
        ministry: "Ministry of Railways",
        state: "Maharashtra",
        sector: "Transport",
        risk: "High",
        cost: "₹1,08,000 Cr",
        progress: 65
    },

    {
        id: 2,
        name: "Dedicated Freight Corridor",
        ministry: "Ministry of Railways",
        state: "Uttar Pradesh",
        sector: "Transport",
        risk: "Medium",
        cost: "₹81,459 Cr",
        progress: 74
    },

    {
        id: 3,
        name: "National River Linking Project",
        ministry: "Ministry of Jal Shakti",
        state: "Madhya Pradesh",
        sector: "Water Resources",
        risk: "High",
        cost: "₹60,000 Cr",
        progress: 42
    },

    {
        id: 4,
        name: "AIIMS Infrastructure Development",
        ministry: "Ministry of Health",
        state: "Delhi",
        sector: "Health",
        risk: "Low",
        cost: "₹15,000 Cr",
        progress: 90
    }

];
document.addEventListener("DOMContentLoaded", function () {

    displayFeaturedProjects();

});
function displayFeaturedProjects() {

    const container =
        document.getElementById("featuredProjects");

    container.innerHTML = featuredProjects
        .slice(0, 3)
        .map(project => {

            return `

                <div class="featured-project-card">

                    <div class="project-card-header">

                        <span class="project-sector">
                            ${project.sector}
                        </span>

                        <span class="risk-badge ${project.risk.toLowerCase()}">
                            ${project.risk} Risk
                        </span>

                    </div>


                    <h3>
                        ${project.name}
                    </h3>


                    <p class="project-ministry">
                        ${project.ministry}
                    </p>


                    <div class="project-info">

                        <div>
                            <span>State</span>
                            <strong>
                                ${project.state}
                            </strong>
                        </div>

                        <div>
                            <span>Project Cost</span>
                            <strong>
                                ${project.cost}
                            </strong>
                        </div>

                    </div>


                    <div class="progress-section">

                        <div class="progress-header">

                            <span>
                                Physical Progress
                            </span>

                            <strong>
                                ${project.progress}%
                            </strong>

                        </div>

                        <div class="progress-bar">

                            <div
                                class="progress-fill"
                                style="width:${project.progress}%">
                            </div>

                        </div>

                    </div>


                    <button
                        class="project-details-btn"
                        onclick="openProject(${project.id})">

                        View Project
                        <span>→</span>

                    </button>

                </div>

            `;

        })
        .join("");
}
function openProject(projectId) {

    window.location.href =
        "project-details.html?id=" + projectId;

}
const projectSearch = document.getElementById("projectName");

projectSearch.addEventListener("input", function () {

    const searchText = this.value.toLowerCase().trim();

    const projects = document.querySelectorAll(".project-row");

    projects.forEach(function (project) {

        const projectName = project
            .querySelector(".project-name")
            .textContent
            .toLowerCase();

        if (projectName.includes(searchText)) {
            project.style.display = "grid";
        } else {
            project.style.display = "none";
        }

    });

});
/* =====================================================
   PROJECT GUARDIAN AUTHENTICATION
===================================================== */


/*
   CHANGE THIS ONLY.

   Example:
   http://localhost:8000

   Or your deployed backend URL.
*/

const API_BASE = "http://localhost:8000";

let registeredEmail = "";

/* =====================================================
   MODEL ANALYSIS AUTH
===================================================== */

/* =====================================================
   AUTH MODAL
===================================================== */

const authModal = document.getElementById("authModal");

const loginForm = document.getElementById("loginForm");

const registerForm = document.getElementById("registerForm");

const authTitle = document.getElementById("authTitle");

const authSubtitle = document.getElementById("authSubtitle");

const authMessage = document.getElementById("authMessage");


/* Open Modal */

function openAuthModal(event) {

    event.preventDefault();

    authModal.style.display = "flex";

    showLogin();

}


/* Close Modal */

function closeAuthModal() {

    authModal.style.display = "none";

    authMessage.innerText = "";

}


/* Show Login */

/* =====================================================
   AUTH TAB SWITCHING
===================================================== */

function showLogin() {

    const loginForm =
        document.getElementById("loginForm");

    const registerForm =
        document.getElementById("registerForm");

    const loginTab =
        document.getElementById("loginTab");

    const registerTab =
        document.getElementById("registerTab");


    registerForm.classList.remove("active");

    loginForm.classList.add("active");


    registerTab.classList.remove("active");

    loginTab.classList.add("active");
}


function showRegister() {

    const loginForm =
        document.getElementById("loginForm");

    const registerForm =
        document.getElementById("registerForm");

    const loginTab =
        document.getElementById("loginTab");

    const registerTab =
        document.getElementById("registerTab");


    loginForm.classList.remove("active");

    registerForm.classList.add("active");


    loginTab.classList.remove("active");

    registerTab.classList.add("active");
}


/* =====================================================
   PASSWORD VISIBILITY
===================================================== */

function togglePassword(inputId, button) {

    const input =
        document.getElementById(inputId);


    if (input.type === "password") {

        input.type = "text";

        button.innerHTML = "🙈";

    } else {

        input.type = "password";

        button.innerHTML = "👁";

    }

}


/* =====================================================
   OPEN MODAL
===================================================== */

function openAuthModal() {

    const modal =
        document.getElementById("authModal");

    modal.classList.add("show");

    showLogin();

}


/* =====================================================
   CLOSE MODAL
===================================================== */

function closeAuthModal() {

    const modal =
        document.getElementById("authModal");

    modal.classList.remove("show");

}
/* =====================================================
   SHOW LOGIN
===================================================== */

function showLoginForm() {

    loginBox.classList.remove("hidden");

    registerBox.classList.add("hidden");

    otpBox.classList.add("hidden");

}


/* =====================================================
   SHOW REGISTER
===================================================== */

function showRegisterForm() {

    loginBox.classList.add("hidden");

    registerBox.classList.remove("hidden");

    otpBox.classList.add("hidden");

}


showRegister.addEventListener(
    "click",
    showRegisterForm
);


showLogin.addEventListener(
    "click",
    showLoginForm
);
/* =====================================================
   REGISTRATION
===================================================== */
registerForm.addEventListener("submit", async function(event) {

    event.preventDefault();


    const username =
        document.getElementById("registerUsername").value.trim();

    const email =
        document.getElementById("registerEmail").value.trim();

    const password =
        document.getElementById("registerPassword").value;

    const role =
        document.getElementById("registerRole").value;

    const department =
        document.getElementById("registerDepartment").value.trim();


    const requestBody = {

        username: username,

        email: email,

        password: password,

        role: role,

        department: department || null

    };


    try {

        const response = await fetch(
            "/api/v1/auth/register",
            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(requestBody)

            }
        );


        const data = await response.json();


        if (response.ok) {

            authMessage.style.color = "green";

            authMessage.innerText =
                "Registration successful. Please verify your email with OTP.";

            /*
             * You can open OTP form here.
             */

            console.log(data);


        } else {

            authMessage.style.color = "red";

            authMessage.innerText =
                data.detail ||
                data.message ||
                "Registration failed.";

        }


    } catch (error) {

        authMessage.style.color = "red";

        authMessage.innerText =
            "Unable to connect to server.";

        console.error(error);

    }

});
/* =====================================================
   OTP VERIFICATION
===================================================== */

const otpForm =
    document.getElementById("otpForm");


otpForm.addEventListener("submit", async function (event) {

    event.preventDefault();


    const email =
        sessionStorage.getItem("registrationEmail");


    const otp_code =
        document.getElementById("otpCode").value.trim();


    if (!/^\d{6}$/.test(otp_code)) {

        alert("OTP must contain exactly 6 digits.");

        return;

    }


    try {

        const response = await fetch(
            "http://localhost:YOUR_PORT/api/v1/auth/verify-otp",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    email: email,

                    otp_code: otp_code

                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            alert(
                data.message ||
                "OTP verification failed."
            );

            return;

        }


        alert(
            "Email verified successfully. You can now login."
        );


        sessionStorage.removeItem(
            "registrationEmail"
        );


        showLoginForm();


    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server."
        );

    }

});
/* =====================================================
   LOGIN
===================================================== */



loginForm.addEventListener("submit", async function(event) {

    event.preventDefault();


    const username =
        document.getElementById("loginUsername").value.trim();

    const password =
        document.getElementById("loginPassword").value;


    try {

        const response = await fetch(
            "/api/v1/auth/login",
            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    username: username,

                    password: password

                })

            }
        );


        const data = await response.json();


        if (response.ok) {

            authMessage.style.color = "green";

            authMessage.innerText =
                "Login successful!";


            /*
             * Open Model Analysis after successful login
             */

            setTimeout(() => {

                closeAuthModal();

                // Change this according to your page
                window.location.href = "#model-analysis";

            }, 1000);


        } else {

            authMessage.style.color = "red";

            authMessage.innerText =
                data.detail ||
                data.message ||
                "Invalid username or password.";

        }


    } catch (error) {

        authMessage.style.color = "red";

        authMessage.innerText =
            "Unable to connect to server.";

        console.error(error);

    }

});
/* =====================================================
   RESEND OTP
===================================================== */

const resendOtp =
    document.getElementById("resendOtp");


resendOtp.addEventListener("click", async function () {

    const email =
        sessionStorage.getItem("registrationEmail");


    if (!email) {

        alert("Email not found.");

        return;

    }


    try {

        const response = await fetch(
            "http://localhost:YOUR_PORT/api/v1/auth/resend-otp",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    email: email

                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            alert(
                data.message ||
                "Unable to resend OTP."
            );

            return;

        }


        alert(
            "A new OTP has been sent to your email."
        );


    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server."
        );

    }

});
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