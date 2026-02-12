/**
 * AegisShare - Client-Side Application
 *
 * Handles authentication, file scanning via the DLP API,
 * and rendering the scan-history dashboard.
 */

"use strict";

/* --------------------------------------------------------------------------
   State
   -------------------------------------------------------------------------- */

/** JWT token received after successful login. */
let authToken = "";

/* --------------------------------------------------------------------------
   DOM References (cached once on load)
   -------------------------------------------------------------------------- */
const DOM = Object.freeze({
  // Login
  loginSection: document.getElementById("loginSection"),
  emailInput: document.getElementById("email"),
  passwordInput: document.getElementById("password"),
  loginError: document.getElementById("loginError"),

  // Upload / Dashboard
  uploadSection: document.getElementById("uploadSection"),
  userDisplay: document.getElementById("userDisplay"),
  fileInput: document.getElementById("fileInput"),

  // Results
  resultArea: document.getElementById("resultArea"),
  statusBadge: document.getElementById("statusBadge"),
  jsonResult: document.getElementById("jsonResult"),

  // History
  historyTableBody: document.getElementById("historyTableBody"),
});

/* --------------------------------------------------------------------------
   API Helpers
   -------------------------------------------------------------------------- */

/**
 * Wrapper around fetch that adds the Authorization header automatically.
 *
 * @param {string}       url     - The request URL.
 * @param {RequestInit}  options - Standard fetch options.
 * @returns {Promise<Response>}
 */
async function apiFetch(url, options = {}) {
  const headers = options.headers || {};
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return fetch(url, { ...options, headers });
}

/* --------------------------------------------------------------------------
   Authentication
   -------------------------------------------------------------------------- */

/**
 * Authenticates the user using email + password and stores the JWT token.
 * On success the view switches from the login form to the upload dashboard.
 */
async function login() {
  const email = DOM.emailInput.value.trim();
  const password = DOM.passwordInput.value;

  if (!email || !password) {
    showLoginError("Por favor, ingresa tu email y contraseña.");
    return;
  }

  // FastAPI's OAuth2PasswordRequestForm expects URL-encoded form data.
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  try {
    const response = await fetch("/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Credenciales inválidas");
    }

    const data = await response.json();
    authToken = data.access_token;

    // Switch to the upload / dashboard view.
    DOM.loginSection.classList.add("hidden");
    DOM.uploadSection.classList.remove("hidden");
    DOM.userDisplay.textContent = email;

    // Pre-load history after login.
    loadHistory();
  } catch (error) {
    showLoginError(error.message);
  }
}

/**
 * Displays an error message beneath the login form.
 *
 * @param {string} message - The error text to show.
 */
function showLoginError(message) {
  DOM.loginError.textContent = message;
  DOM.loginError.classList.remove("hidden");
}

/* --------------------------------------------------------------------------
   File Scanning
   -------------------------------------------------------------------------- */

/**
 * Reads the selected file, sends it to the DLP scan endpoint, and renders
 * the analysis result (approved / blocked) along with detail JSON.
 */
async function uploadFile() {
  const file = DOM.fileInput.files[0];
  if (!file) return;

  // Show loading state.
  setStatusBadge("Analizando con IA…", "loading");
  DOM.resultArea.classList.remove("hidden");

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiFetch("/scan/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Error en el análisis del archivo.");
    }

    const data = await response.json();
    const isBlocked = data.analisis_ia.includes("BLOQUEADO");

    setStatusBadge(data.analisis_ia, isBlocked ? "blocked" : "safe");
    DOM.jsonResult.textContent = JSON.stringify(data.detalles, null, 2);

    // Refresh history to include the new scan.
    loadHistory();
  } catch (error) {
    console.error("Error uploading file:", error);
    setStatusBadge("Error al analizar el archivo.", "blocked");
  } finally {
    // Reset file input so the same file can be re-selected.
    DOM.fileInput.value = "";
  }
}

/**
 * Updates the status badge text and visual style.
 *
 * @param {string} text   - The message to display.
 * @param {"loading"|"safe"|"blocked"} variant - Visual variant.
 */
function setStatusBadge(text, variant) {
  DOM.statusBadge.textContent = text;
  DOM.statusBadge.className = `status-badge status-badge--${variant}`;
}

/* --------------------------------------------------------------------------
   History Dashboard
   -------------------------------------------------------------------------- */

/**
 * Fetches the current user's scan history and renders it in the history table.
 */
async function loadHistory() {
  try {
    const response = await apiFetch("/history/");

    if (!response.ok) {
      throw new Error("Error al cargar el historial.");
    }

    const logs = await response.json();
    renderHistory(logs);
  } catch (error) {
    console.error("Error loading history:", error);
  }
}

/**
 * Renders an array of scan-log objects into the history table body.
 * Uses textContent instead of innerHTML for XSS safety.
 *
 * @param {Array<{filename: string, status: string, timestamp: string}>} logs
 */
function renderHistory(logs) {
  // Clear previous rows.
  DOM.historyTableBody.innerHTML = "";

  const fragment = document.createDocumentFragment();

  logs.forEach((log) => {
    const row = document.createElement("tr");

    const isBlocked = log.status.includes("BLOQUEADO");

    // Filename cell
    const filenameCell = document.createElement("td");
    filenameCell.className = "text--filename";
    filenameCell.textContent = log.filename;

    // Status cell
    const statusCell = document.createElement("td");
    statusCell.className = isBlocked ? "text--blocked" : "text--safe";
    statusCell.textContent = log.status;

    // Timestamp cell
    const timestampCell = document.createElement("td");
    timestampCell.className = "text--timestamp";
    timestampCell.textContent = new Date(log.timestamp).toLocaleString();

    row.append(filenameCell, statusCell, timestampCell);
    fragment.appendChild(row);
  });

  DOM.historyTableBody.appendChild(fragment);
}

/* --------------------------------------------------------------------------
   Dropzone click delegation
   -------------------------------------------------------------------------- */

/**
 * Opens the native file picker when the dropzone area is clicked.
 */
function openFilePicker() {
  DOM.fileInput.click();
}
