/**
 * RISKLENS / PROJECT GUARDIAN - AUTHENTICATION & OTP WORKFLOW MODULE
 * File: js/auth-otp-handler.js
 * Mirrors js/auth.js with immediate DOM view transition on Register submit
 */

(function () {
  'use strict';

  // Prevent legacy script crashes
  if (typeof window.showRegister === 'undefined' || typeof window.showRegister?.addEventListener !== 'function') {
    window.showRegister = { addEventListener: function () {} };
  }
  if (typeof window.showLogin === 'undefined' || typeof window.showLogin?.addEventListener !== 'function') {
    window.showLogin = { addEventListener: function () {} };
  }

  const AUTH_CONFIG = {
    BASE_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? (window.location.port === '8000' ? '/api/v1' : 'http://127.0.0.1:8000/api/v1')
      : '/api/v1',
    OTP_EXPIRE_MINUTES: 2,
    OTP_RESEND_COOLDOWN_SECONDS: 60
  };

  let otpExpireInterval = null;
  let resendCooldownInterval = null;
  let otpExpireSecondsRemaining = AUTH_CONFIG.OTP_EXPIRE_MINUTES * 60;

  function showFeedback(formId, message, type = 'info') {
    let banner = document.getElementById(`${formId}FeedbackBanner`) || document.getElementById('otpFeedbackBanner');
    if (!banner) {
      const form = document.getElementById(formId);
      if (form) {
        banner = document.createElement('div');
        banner.id = `${formId}FeedbackBanner`;
        banner.className = 'auth-feedback-banner';
        const subtitle = form.querySelector('.form-subtitle');
        if (subtitle && subtitle.nextSibling) {
          form.insertBefore(banner, subtitle.nextSibling);
        } else {
          form.prepend(banner);
        }
      }
    }

    if (banner) {
      banner.className = `auth-feedback-banner show ${type}`;
      banner.textContent = message;
    }
  }

  function clearFeedback(formId) {
    const banner = document.getElementById(`${formId}FeedbackBanner`) || document.getElementById('otpFeedbackBanner');
    if (banner) {
      banner.className = 'auth-feedback-banner';
      banner.textContent = '';
    }
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  function startExpirationTimer() {
    if (otpExpireInterval) {
      clearInterval(otpExpireInterval);
    }

    otpExpireSecondsRemaining = AUTH_CONFIG.OTP_EXPIRE_MINUTES * 60;
    const countElem = document.getElementById('otpExpireCountdown');
    const timerContainer = document.getElementById('otpExpirationLine');
    const submitBtn = document.getElementById('otpSubmitBtn');

    if (timerContainer) timerContainer.classList.remove('expired');
    if (countElem) countElem.textContent = formatTime(otpExpireSecondsRemaining);
    if (submitBtn) submitBtn.disabled = false;

    otpExpireInterval = setInterval(() => {
      otpExpireSecondsRemaining -= 1;

      if (otpExpireSecondsRemaining <= 0) {
        clearInterval(otpExpireInterval);
        otpExpireInterval = null;
        if (countElem) countElem.textContent = '00:00';
        if (timerContainer) timerContainer.classList.add('expired');
        if (submitBtn) submitBtn.disabled = true;
        showFeedback('otpForm', 'OTP expired. Please click "Resend OTP" to receive a fresh code.', 'error');
      } else {
        if (countElem) countElem.textContent = formatTime(otpExpireSecondsRemaining);
      }
    }, 1000);
  }

  function startResendCooldown() {
    const resendBtn = document.getElementById('resendOtpBtn');
    if (!resendBtn) return;

    if (resendCooldownInterval) {
      clearInterval(resendCooldownInterval);
    }

    let remaining = AUTH_CONFIG.OTP_RESEND_COOLDOWN_SECONDS;
    resendBtn.disabled = true;
    resendBtn.textContent = `Resend in ${remaining}s`;

    resendCooldownInterval = setInterval(() => {
      remaining -= 1;

      if (remaining <= 0) {
        clearInterval(resendCooldownInterval);
        resendCooldownInterval = null;
        resendBtn.disabled = false;
        resendBtn.textContent = 'Resend OTP';
      } else {
        resendBtn.textContent = `Resend in ${remaining}s`;
      }
    }, 1000);
  }

  function startBothTimers() {
    startExpirationTimer();
    startResendCooldown();
  }

  function stopAllTimers() {
    if (otpExpireInterval) {
      clearInterval(otpExpireInterval);
      otpExpireInterval = null;
    }
    if (resendCooldownInterval) {
      clearInterval(resendCooldownInterval);
      resendCooldownInterval = null;
    }
    const resendBtn = document.getElementById('resendOtpBtn');
    if (resendBtn) {
      resendBtn.disabled = false;
      resendBtn.textContent = 'Resend OTP';
    }
  }

  function setupOtpDigitInputs() {
    const container = document.getElementById('otpBoxesContainer');
    if (!container) return;

    const digits = container.querySelectorAll('.otp-digit, .otp-box-digit');
    const hiddenOtpInput = document.getElementById('otpCode');

    function syncHiddenInput() {
      let code = '';
      digits.forEach(d => {
        code += (d.value || '');
      });
      if (hiddenOtpInput) {
        hiddenOtpInput.value = code;
      }
      return code;
    }

    digits.forEach((input, index) => {
      input.addEventListener('input', () => {
        const val = input.value.replace(/[^0-9]/g, '');
        input.value = val ? val.slice(-1) : '';

        if (input.value) {
          input.classList.add('filled');
          if (index < digits.length - 1) {
            digits[index + 1].focus();
            digits[index + 1].select();
          }
        } else {
          input.classList.remove('filled');
        }

        syncHiddenInput();
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace') {
          if (!input.value && index > 0) {
            digits[index - 1].focus();
            digits[index - 1].value = '';
            digits[index - 1].classList.remove('filled');
            e.preventDefault();
          } else {
            input.value = '';
            input.classList.remove('filled');
          }
          syncHiddenInput();
        } else if (e.key === 'ArrowLeft' && index > 0) {
          digits[index - 1].focus();
        } else if (e.key === 'ArrowRight' && index < digits.length - 1) {
          digits[index + 1].focus();
        }
      });

      input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pastedData = (e.clipboardData || window.clipboardData).getData('text').trim();
        const cleanDigits = pastedData.replace(/[^0-9]/g, '').slice(0, 6);

        if (cleanDigits) {
          cleanDigits.split('').forEach((char, i) => {
            if (digits[i]) {
              digits[i].value = char;
              digits[i].classList.add('filled');
            }
          });
          syncHiddenInput();
          const targetIndex = Math.min(cleanDigits.length, digits.length - 1);
          digits[targetIndex].focus();
        }
      });
    });
  }

  function getEnteredOtpCode() {
    const hidden = document.getElementById('otpCode');
    if (hidden && hidden.value && hidden.value.length === 6) {
      return hidden.value;
    }

    const container = document.getElementById('otpBoxesContainer');
    if (container) {
      let code = '';
      container.querySelectorAll('.otp-digit, .otp-box-digit').forEach(d => {
        code += (d.value || '');
      });
      return code.trim();
    }

    return '';
  }

  function clearOtpInputs() {
    const container = document.getElementById('otpBoxesContainer');
    if (container) {
      container.querySelectorAll('.otp-digit, .otp-box-digit').forEach(d => {
        d.value = '';
        d.classList.remove('filled');
      });
    }
    const hidden = document.getElementById('otpCode');
    if (hidden) hidden.value = '';
  }

  function focusFirstOtpDigit() {
    const container = document.getElementById('otpBoxesContainer');
    if (container) {
      const first = container.querySelector('.otp-digit, .otp-box-digit');
      if (first) {
        setTimeout(() => {
          first.focus();
          first.select?.();
        }, 120);
      }
    }
  }

  function showLoginForm() {
    stopAllTimers();
    clearFeedback('loginForm');
    clearFeedback('registerForm');
    clearFeedback('otpForm');

    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const otpForm = document.getElementById('otpForm');
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');

    if (loginForm) {
      loginForm.classList.add('active');
      loginForm.classList.remove('hidden');
      loginForm.style.display = 'block';
    }
    if (registerForm) {
      registerForm.classList.remove('active');
      registerForm.classList.add('hidden');
      registerForm.style.display = 'none';
    }
    if (otpForm) {
      otpForm.classList.remove('active');
      otpForm.classList.add('hidden');
      otpForm.style.display = 'none';
    }

    if (loginTab) loginTab.classList.add('active');
    if (registerTab) registerTab.classList.remove('active');
  }

  function showRegisterForm() {
    stopAllTimers();
    clearFeedback('loginForm');
    clearFeedback('registerForm');
    clearFeedback('otpForm');

    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const otpForm = document.getElementById('otpForm');
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');

    if (loginForm) {
      loginForm.classList.remove('active');
      loginForm.classList.add('hidden');
      loginForm.style.display = 'none';
    }
    if (registerForm) {
      registerForm.classList.add('active');
      registerForm.classList.remove('hidden');
      registerForm.style.display = 'block';
    }
    if (otpForm) {
      otpForm.classList.remove('active');
      otpForm.classList.add('hidden');
      otpForm.style.display = 'none';
    }

    if (loginTab) loginTab.classList.remove('active');
    if (registerTab) registerTab.classList.add('active');
  }

  function showOtpVerificationView(email) {
    clearFeedback('loginForm');
    clearFeedback('registerForm');
    clearFeedback('otpForm');

    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const otpForm = document.getElementById('otpForm');
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');

    if (loginForm) {
      loginForm.classList.remove('active');
      loginForm.classList.add('hidden');
      loginForm.style.display = 'none';
    }
    if (registerForm) {
      registerForm.classList.remove('active');
      registerForm.classList.add('hidden');
      registerForm.style.display = 'none';
    }
    if (otpForm) {
      otpForm.classList.add('active');
      otpForm.classList.remove('hidden');
      otpForm.style.display = 'block';
    }

    if (loginTab) loginTab.classList.remove('active');
    if (registerTab) registerTab.classList.remove('active');

    const targetEmail = email || sessionStorage.getItem('pending_otp_email') || 'your email';
    const emailDisplay = document.getElementById('otpTargetEmailDisplay');
    if (emailDisplay) {
      emailDisplay.textContent = targetEmail;
    }

    clearOtpInputs();
    focusFirstOtpDigit();
    startBothTimers();
  }

  function handleRegisterTransition(event) {
    if (event) {
      event.preventDefault();
      event.stopImmediatePropagation?.();
      event.stopPropagation?.();
    }

    clearFeedback('registerForm');

    const username = document.getElementById('registerUsername')?.value?.trim() || '';
    const email = document.getElementById('registerEmail')?.value?.trim() || '';
    const password = document.getElementById('registerPassword')?.value || '';
    const role = document.getElementById('registerRole')?.value?.trim() || 'Monitoring Officer';
    const department = document.getElementById('registerDepartment')?.value?.trim() || null;

    if (!username || !email || !password) {
      showFeedback('registerForm', 'Please fill in all required fields (Username, Email, Password).', 'error');
      return false;
    }

    sessionStorage.setItem('pending_otp_email', email);
    showOtpVerificationView(email);

    fetch(`${AUTH_CONFIG.BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, role, department })
    })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}));
      if (res.status === 201 || res.ok) {
        showFeedback('otpForm', `OTP sent to ${email}. Please enter the 6-digit code.`, 'success');
      } else {
        const errorMsg = data.detail || data.message;
        if (errorMsg && errorMsg.toLowerCase().includes('already registered')) {
          showFeedback('otpForm', `${errorMsg}. Please enter your existing OTP or click Resend.`, 'info');
        } else if (errorMsg) {
          showFeedback('otpForm', errorMsg, 'error');
        }
      }
    })
    .catch((err) => {
      console.warn('Background registration request notice:', err);
    });

    return false;
  }

  async function handleVerifyOtp(event) {
    if (event) {
      event.preventDefault();
      event.stopImmediatePropagation?.();
      event.stopPropagation?.();
    }

    clearFeedback('otpForm');

    const email = sessionStorage.getItem('pending_otp_email') ||
                  document.getElementById('otpTargetEmailDisplay')?.textContent?.trim() ||
                  document.getElementById('registerEmail')?.value?.trim();

    const otp_code = getEnteredOtpCode();
    const submitBtn = document.getElementById('otpSubmitBtn');

    if (!email) {
      showFeedback('otpForm', 'Verification email not found. Please click Register to restart.', 'error');
      return;
    }

    if (!/^\d{6}$/.test(otp_code)) {
      showFeedback('otpForm', 'Please enter a valid 6-digit numeric OTP code.', 'error');
      focusFirstOtpDigit();
      return;
    }

    const origBtnText = submitBtn ? submitBtn.innerHTML : 'Verify OTP';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Verifying Code...';
    }

    try {
      const response = await fetch(`${AUTH_CONFIG.BASE_URL}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp_code })
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        stopAllTimers();
        sessionStorage.removeItem('pending_otp_email');

        showLoginForm();
        showFeedback('loginForm', 'Email verified successfully! Please log in with your credentials.', 'success');

        const regUsername = document.getElementById('registerUsername')?.value?.trim();
        const loginUsername = document.getElementById('loginUsername');
        if (loginUsername && regUsername) {
          loginUsername.value = regUsername;
          document.getElementById('loginPassword')?.focus();
        }
      } else {
        const errorMsg = data.detail || data.message || 'Invalid or expired OTP code. Please try again.';
        showFeedback('otpForm', errorMsg, 'error');
        clearOtpInputs();
        focusFirstOtpDigit();
      }
    } catch (err) {
      console.error('OTP verify network error:', err);
      showFeedback('otpForm', 'Connection error while verifying OTP.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = origBtnText;
      }
    }
  }

  async function handleResendOtp(event) {
    if (event) {
      event.preventDefault();
      event.stopImmediatePropagation?.();
      event.stopPropagation?.();
    }

    const email = sessionStorage.getItem('pending_otp_email') ||
                  document.getElementById('otpTargetEmailDisplay')?.textContent?.trim() ||
                  document.getElementById('registerEmail')?.value?.trim();

    const resendBtn = document.getElementById('resendOtpBtn');

    if (!email) {
      showFeedback('otpForm', 'Pending email not found. Please click Register to restart.', 'error');
      return;
    }

    if (resendBtn) {
      resendBtn.disabled = true;
      resendBtn.textContent = 'Sending OTP...';
    }

    try {
      const response = await fetch(`${AUTH_CONFIG.BASE_URL}/auth/resend-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        showFeedback('otpForm', `A fresh 6-digit OTP has been sent to ${email}`, 'info');
        clearOtpInputs();
        focusFirstOtpDigit();
        startBothTimers();
      } else {
        const errorMsg = data.detail || data.message || 'Failed to resend OTP. Please wait and try again.';
        showFeedback('otpForm', errorMsg, 'error');
        if (resendBtn) {
          resendBtn.disabled = false;
          resendBtn.textContent = 'Resend OTP';
        }
      }
    } catch (err) {
      console.error('Resend OTP network error:', err);
      showFeedback('otpForm', 'Network error requesting OTP resend.', 'error');
      if (resendBtn) {
        resendBtn.disabled = false;
        resendBtn.textContent = 'Resend OTP';
      }
    }
  }

  async function handleLogin(event) {
    if (event) {
      event.preventDefault();
      event.stopImmediatePropagation?.();
      event.stopPropagation?.();
    }

    clearFeedback('loginForm');

    const username = document.getElementById('loginUsername')?.value?.trim() || '';
    const password = document.getElementById('loginPassword')?.value || '';
    const submitBtn = document.querySelector('#loginForm button[type="submit"]');

    if (!username || !password) {
      showFeedback('loginForm', 'Please enter your username and password.', 'error');
      return;
    }

    const origBtnText = submitBtn ? submitBtn.innerHTML : 'Login';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Authenticating...';
    }

    try {
      const response = await fetch(`${AUTH_CONFIG.BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok && data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token', data.access_token);
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
          localStorage.setItem('username', data.user.username);
        }

        showFeedback('loginForm', 'Login successful! Redirecting to Model Analysis...', 'success');
        setTimeout(() => {
          window.location.href = 'model-analysis.html';
        }, 800);
      } else {
        const errorMsg = data.detail || data.message || 'Authentication failed. Please check credentials.';
        showFeedback('loginForm', errorMsg, 'error');

        if (response.status === 403 || errorMsg.toLowerCase().includes('email verification required') || errorMsg.toLowerCase().includes('otp')) {
          const pendingEmail = sessionStorage.getItem('pending_otp_email');
          setTimeout(() => {
            showOtpVerificationView(pendingEmail || username);
            showFeedback('otpForm', 'Email verification required. Please enter the OTP sent to your email.', 'error');
          }, 1200);
        }
      }
    } catch (err) {
      console.error('Login network error:', err);
      showFeedback('loginForm', 'Connection error reaching authentication service.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = origBtnText;
      }
    }
  }

  function initAuthWiring() {
    setupOtpDigitInputs();

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
      registerForm.addEventListener('submit', handleRegisterTransition, { capture: true });
    }

    const otpForm = document.getElementById('otpForm');
    if (otpForm) {
      otpForm.addEventListener('submit', handleVerifyOtp, { capture: true });
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      loginForm.addEventListener('submit', handleLogin, { capture: true });
    }

    const resendBtn = document.getElementById('resendOtpBtn');
    if (resendBtn) {
      resendBtn.addEventListener('click', handleResendOtp, { capture: true });
    }

    const loginTab = document.getElementById('loginTab');
    if (loginTab) {
      loginTab.addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
      });
    }

    const registerTab = document.getElementById('registerTab');
    if (registerTab) {
      registerTab.addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
      });
    }

    window.showRegister = showRegisterForm;
    window.showLogin = showLoginForm;
    window.showOtpForm = showOtpVerificationView;
    window.registerUser = handleRegisterTransition;
    window.verifyOtp = handleVerifyOtp;
    window.resendOtp = handleResendOtp;
    window.loginUser = handleLogin;

    window.openAuthModal = function (event) {
      if (event) event.preventDefault();
      const modal = document.getElementById('authModal');
      if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
        showLoginForm();
      }
    };

    window.closeAuthModal = function (event) {
      if (event) event.preventDefault();
      const modal = document.getElementById('authModal');
      if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
        stopAllTimers();
      }
    };

    const pendingEmail = sessionStorage.getItem('pending_otp_email');
    if (pendingEmail) {
      const emailDisplay = document.getElementById('otpTargetEmailDisplay');
      if (emailDisplay) emailDisplay.textContent = pendingEmail;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuthWiring);
  } else {
    initAuthWiring();
  }

})();
