console.log("Main.js global execution started");
// alert("Main.js is connected!"); 
function initValidation() {
    console.log("Validation script initializing...");
    const nameInput = document.getElementById("nameInput");
    const phoneInput = document.getElementById("phoneInput");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const cpasswordInput = document.getElementById("cpasswordInput");
    const registerForm = document.getElementById("registerform");
    const submitError = document.getElementById("submitError");

    function validateName() {
        if (nameInput.value.trim().length <= 2) {
            document.getElementById("nameError").innerText = "Name must be at least 3 characters long.";
            return false;
        } else {
            document.getElementById("nameError").innerText = "";
            return true;
        }
    }

    function validatePhone() {
        const phoneVal = phoneInput.value.trim();
        // Regex to check for non-numeric characters
        const nonNumericRegex = /[^\d]/; 
        // Regex to check for exactly 10 digits
        const phoneRegex = /^\d{10}$/;
        
        if (nonNumericRegex.test(phoneVal)) {
            document.getElementById("phoneError").innerText = "Only accept numbers.";
            return false;
        } else if (!phoneRegex.test(phoneVal)) {
            document.getElementById("phoneError").innerText = "Phone number must be exactly 10 digits.";
            return false;
        } else {
            document.getElementById("phoneError").innerText = "";
            return true;
        }
    }

    function validateEmail() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value.trim())) {
            document.getElementById("emailError").innerText = "Invalid email format.";
            return false;
        } else {
            document.getElementById("emailError").innerText = "";
            return true;
        }
    }

    function validatePassword() {
        const pwd = passwordInput.value;
        const msgSpan = document.getElementById("passwordError");
        if (pwd.length <= 6) {
            msgSpan.innerText = "Password must be more than 6 characters long.";
            return false;
        }
        if (!/[a-z]/.test(pwd)) {
            msgSpan.innerText = "Password must contain at least one small letter.";
            return false;
        }
        if (!/[A-Z]/.test(pwd)) {
            msgSpan.innerText = "Password must contain at least one capital letter.";
            return false;
        }
        if (!/[0-9]/.test(pwd)) {
            msgSpan.innerText = "Password must contain at least one number.";
            return false;
        }
        const specialChars = /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
        if (!specialChars.test(pwd)) {
            msgSpan.innerText = "Password must contain at least one symbol (e.g., @, #).";
            return false;
        }
        msgSpan.innerText = "";
        return true;
    }

    function validateCPassword() {
        if (cpasswordInput.value !== passwordInput.value) {
            document.getElementById("cpasswordError").innerText = "Passwords do not match.";
            return false;
        } else {
            document.getElementById("cpasswordError").innerText = "";
            return true;
        }
    }

    if(nameInput) nameInput.addEventListener("input", validateName);
    if(phoneInput) phoneInput.addEventListener("input", validatePhone);
    if(emailInput) emailInput.addEventListener("input", validateEmail);
    if(passwordInput) passwordInput.addEventListener("input", validatePassword);
    if(cpasswordInput) cpasswordInput.addEventListener("input", validateCPassword);

    if(registerForm) {
        registerForm.addEventListener("submit", function(event) {
            const isNameValid = validateName();
            const isPhoneValid = validatePhone();
            const isEmailValid = validateEmail();
            const isPasswordValid = validatePassword();
            const isCPasswordValid = validateCPassword();

            if (!isNameValid || !isPhoneValid || !isEmailValid || !isPasswordValid || !isCPasswordValid) {
                event.preventDefault(); 
                submitError.style.display = "block";
            } else {
                submitError.style.display = "none";
            }
        });
    }
}

// Run immediately if DOM is ready, otherwise wait for load
if (document.readyState === "complete" || document.readyState === "interactive") {
    initValidation();
    initLoginValidation();
    initChangePwdValidation();
    initResetPwdValidation();
} else {
    document.addEventListener("DOMContentLoaded", function() {
        initValidation();
        initLoginValidation();
        initChangePwdValidation();
        initResetPwdValidation();
    });
}

/* ========== Shared: Password Strength Checker ========== */
function checkPasswordStrength(pwd, spanEl) {
    if (pwd.length <= 6) {
        spanEl.innerText = "Password must be more than 6 characters long.";
        return false;
    }
    if (!/[a-z]/.test(pwd)) {
        spanEl.innerText = "Password must contain at least one small letter.";
        return false;
    }
    if (!/[A-Z]/.test(pwd)) {
        spanEl.innerText = "Password must contain at least one capital letter.";
        return false;
    }
    if (!/[0-9]/.test(pwd)) {
        spanEl.innerText = "Password must contain at least one number.";
        return false;
    }
    const specialChars = /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
    if (!specialChars.test(pwd)) {
        spanEl.innerText = "Password must contain at least one symbol (e.g., @, #).";
        return false;
    }
    spanEl.innerText = "";
    return true;
}

/* ========== Change Password Page Validation ========== */
function initChangePwdValidation() {
    const form = document.getElementById("changepwdform");
    if (!form) return; // Only run on change password page

    const oldPwdInput    = document.getElementById("oldPwdInput");
    const newPwdInput    = document.getElementById("newPwdInput");
    const confirmPwdInput = document.getElementById("confirmPwdInput");
    const submitError    = document.getElementById("changePwdSubmitError");

    function validateOldPwd() {
        const err = document.getElementById("oldPwdError");
        if (!oldPwdInput.value) {
            err.innerText = "Old password is required.";
            return false;
        }
        err.innerText = "";
        return true;
    }

    function validateNewPwd() {
        return checkPasswordStrength(newPwdInput.value, document.getElementById("newPwdError"));
    }

    function validateConfirmPwd() {
        const err = document.getElementById("confirmPwdError");
        if (confirmPwdInput.value !== newPwdInput.value) {
            err.innerText = "Passwords do not match.";
            return false;
        }
        err.innerText = "";
        return true;
    }

    oldPwdInput.addEventListener("input", validateOldPwd);
    newPwdInput.addEventListener("input", validateNewPwd);
    confirmPwdInput.addEventListener("input", validateConfirmPwd);

    form.addEventListener("submit", function(event) {
        const v1 = validateOldPwd();
        const v2 = validateNewPwd();
        const v3 = validateConfirmPwd();

        if (!v1 || !v2 || !v3) {
            event.preventDefault();
            submitError.style.display = "block";
        } else {
            submitError.style.display = "none";
        }
    });
}

/* ========== Reset Password Page Validation ========== */
function initResetPwdValidation() {
    const form = document.getElementById("resetpwdform");
    if (!form) return; // Only run on reset password page

    const pwdInput     = document.getElementById("resetPwdInput");
    const confirmInput = document.getElementById("resetConfirmPwdInput");
    const submitError  = document.getElementById("resetPwdSubmitError");

    function validateResetPwd() {
        return checkPasswordStrength(pwdInput.value, document.getElementById("resetPwdError"));
    }

    function validateResetConfirm() {
        const err = document.getElementById("resetConfirmPwdError");
        if (confirmInput.value !== pwdInput.value) {
            err.innerText = "Passwords do not match.";
            return false;
        }
        err.innerText = "";
        return true;
    }

    pwdInput.addEventListener("input", validateResetPwd);
    confirmInput.addEventListener("input", validateResetConfirm);

    form.addEventListener("submit", function(event) {
        const v1 = validateResetPwd();
        const v2 = validateResetConfirm();

        if (!v1 || !v2) {
            event.preventDefault();
            submitError.style.display = "block";
        } else {
            submitError.style.display = "none";
        }
    });
}

/* ========== Login Page Validation ========== */
function initLoginValidation() {
    const loginForm = document.getElementById("loginform");
    const loginEmailInput = document.getElementById("loginEmailInput");
    const loginPasswordInput = document.getElementById("loginPasswordInput");
    const loginSubmitError = document.getElementById("loginSubmitError");

    if (!loginForm) return; // Only run on login page

    function validateLoginEmail() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const emailError = document.getElementById("loginEmailError");
        if (!loginEmailInput.value.trim()) {
            emailError.innerText = "Email is required.";
            return false;
        } else if (!emailRegex.test(loginEmailInput.value.trim())) {
            emailError.innerText = "Invalid email format.";
            return false;
        } else {
            emailError.innerText = "";
            return true;
        }
    }

    function validateLoginPassword() {
        const pwdError = document.getElementById("loginPasswordError");
        if (!loginPasswordInput.value) {
            pwdError.innerText = "Password is required.";
            return false;
        } else if (loginPasswordInput.value.length < 6) {
            pwdError.innerText = "Password must be at least 6 characters.";
            return false;
        } else {
            pwdError.innerText = "";
            return true;
        }
    }

    loginEmailInput.addEventListener("input", validateLoginEmail);
    loginPasswordInput.addEventListener("input", validateLoginPassword);

    loginForm.addEventListener("submit", function(event) {
        const isEmailValid = validateLoginEmail();
        const isPasswordValid = validateLoginPassword();

        if (!isEmailValid || !isPasswordValid) {
            event.preventDefault();
            loginSubmitError.style.display = "block";
        } else {
            loginSubmitError.style.display = "none";
        }
    });
}
