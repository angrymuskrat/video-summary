const apiBase = "/api";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function getJson(path) {
  const response = await fetch(`${apiBase}${path}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }
  return response.json();
}

function statusTone(status) {
  if (status === "completed") return "ok";
  if (status === "failed") return "bad";
  return "";
}

function humanDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

function renderNav(active) {
  document.querySelectorAll(".nav-links a").forEach((link) => {
    if (link.dataset.page === active) {
      link.classList.add("active");
    }
  });
}

function formField(field) {
  if (field.kind === "checkbox") {
    return `
      <label class="checkbox field full">
        <input type="checkbox" name="${field.name}" ${field.default ? "checked" : ""}>
        <span>
          <strong>${escapeHtml(field.label)}</strong>
          ${field.help ? `<small>${escapeHtml(field.help)}</small>` : ""}
        </span>
      </label>
    `;
  }

  const options = (field.options || [])
    .map((option) => `<option value="${escapeHtml(option)}" ${option === field.default ? "selected" : ""}>${escapeHtml(option)}</option>`)
    .join("");
  const input =
    field.kind === "select"
      ? `<select name="${field.name}">${options}</select>`
      : `<input name="${field.name}" type="${field.kind}" value="${field.default ?? ""}" ${field.placeholder ? `placeholder="${escapeHtml(field.placeholder)}"` : ""} ${field.step ? `step="${field.step}"` : ""}>`;
  return `
    <label class="field">
      <span>${escapeHtml(field.label)}</span>
      ${input}
      ${field.help ? `<small>${escapeHtml(field.help)}</small>` : ""}
    </label>
  `;
}

function renderJobMeta(job) {
  const artifacts = job.artifacts || [];
  return `
    <div class="status-strip">
      <span class="status-badge ${statusTone(job.status)}">${escapeHtml(job.status)}</span>
      ${job.current_step ? `<span class="status-badge">step: ${escapeHtml(job.current_step)}</span>` : ""}
      <span class="status-badge">${artifacts.length} artifact(s)</span>
    </div>
    <div class="meta-list" style="margin-top:16px;">
      <div class="meta-item"><strong>Job ID</strong><div class="code">${escapeHtml(job.job_id)}</div></div>
      <div class="meta-item"><strong>Source File</strong><div>${escapeHtml(job.input_filename)}</div></div>
      <div class="meta-item"><strong>Created</strong><div>${escapeHtml(humanDate(job.created_at))}</div></div>
      <div class="meta-item"><strong>Started</strong><div>${escapeHtml(humanDate(job.started_at))}</div></div>
      <div class="meta-item"><strong>Finished</strong><div>${escapeHtml(humanDate(job.finished_at))}</div></div>
      <div class="meta-item"><strong>Expires</strong><div>${escapeHtml(humanDate(job.expires_at))}</div></div>
      ${job.error_message ? `<div class="meta-item error"><strong>Failure</strong><div>${escapeHtml(job.error_message)}</div></div>` : ""}
    </div>
  `;
}

function renderArtifactList(job) {
  const artifacts = job.artifacts || [];
  if (!artifacts.length) {
    return `<div class="empty-box">Artifacts will appear here after the pipeline produces files.</div>`;
  }
  return `
    <div class="artifact-list">
      ${artifacts
        .map(
          (artifact) => `
            <article class="artifact-item">
              <div>
                <strong>${escapeHtml(artifact.name)}</strong>
                <div class="muted">${escapeHtml(artifact.kind)} · ${artifact.size_bytes ?? "?"} bytes</div>
              </div>
              <div class="artifact-actions">
                <a class="button secondary" href="${escapeHtml(artifact.download_url)}">Download</a>
                ${
                  artifact.previewable
                    ? `<button class="secondary artifact-preview" type="button" data-url="${escapeHtml(artifact.preview_url)}" data-name="${escapeHtml(artifact.name)}">Preview</button>`
                    : ""
                }
              </div>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

async function initUploadPage() {
  renderNav("upload");
  const container = byId("upload-app");
  const resultBox = byId("upload-result");
  const info = await getJson("/form-options");
  byId("retention-copy").textContent = `${info.retention_hours} hours`;
  byId("openai-copy").textContent = info.openai_summary_available ? "enabled on server" : "disabled until OPENAI_* env vars are set";
  container.innerHTML = `
    <form id="upload-form" class="card">
      <div class="eyebrow">Pipeline launch form</div>
      <h2 class="section-title">Upload a meeting file and start a tracked job</h2>
      <p class="muted">Server-side OpenAI settings stay hidden here; the form only exposes user-controlled pipeline flags and tuning values.</p>
      <label class="field full" style="margin-bottom:18px;">
        <span>Input File</span>
        <input name="file" type="file" required>
        <small>Upload `.webm`, `.mp4`, or another file your pipeline accepts.</small>
      </label>
      <div class="form-grid">${info.fields.map(formField).join("")}</div>
      <div class="hero-actions" style="margin-top:22px;">
        <button class="primary" type="submit">Start Pipeline Job</button>
      </div>
    </form>
  `;

  byId("upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    resultBox.innerHTML = `<div class="empty-box">Submitting job…</div>`;
    const formElement = event.currentTarget;
    const formData = new FormData();
    const fileInput = formElement.querySelector('input[name="file"]');
    if (!fileInput.files.length) {
      resultBox.innerHTML = `<div class="empty-box error">Choose a file before submitting.</div>`;
      return;
    }
    formData.append("file", fileInput.files[0]);
    const controls = formElement.querySelectorAll("input, select");
    controls.forEach((control) => {
      if (control.name === "file") return;
      if (control.type === "checkbox") {
        if (control.checked) {
          formData.append(control.name, "true");
        }
        return;
      }
      if (control.value !== "") {
        formData.append(control.name, control.value);
      }
    });

    try {
      const response = await fetch(`${apiBase}/jobs`, { method: "POST", body: formData });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || `Request failed with ${response.status}`);
      }
      resultBox.innerHTML = `
        <div class="result-box">
          <strong>Job queued</strong>
          <div class="code" style="margin:10px 0 16px;">${escapeHtml(payload.job_id)}</div>
          <div class="hero-actions">
            <a class="button" href="/status.html?id=${encodeURIComponent(payload.job_id)}">Open status page</a>
            <a class="button secondary" href="/artifacts.html?id=${encodeURIComponent(payload.job_id)}">Open artifacts page</a>
          </div>
        </div>
      `;
    } catch (error) {
      resultBox.innerHTML = `<div class="result-box error">${escapeHtml(error.message)}</div>`;
    }
  });
}

async function initStatusPage() {
  renderNav("status");
  const form = byId("status-form");
  const input = byId("status-job-id");
  const output = byId("status-output");
  const params = new URLSearchParams(window.location.search);
  if (params.get("id")) {
    input.value = params.get("id");
  }

  let refreshTimer = null;
  async function loadStatus() {
    if (!input.value.trim()) return;
    output.innerHTML = `<div class="empty-box">Loading job status…</div>`;
    try {
      const job = await getJson(`/jobs/${encodeURIComponent(input.value.trim())}`);
      output.innerHTML = `
        <div class="two-column">
          <section class="card">${renderJobMeta(job)}</section>
          <section class="card">
            <h2 class="section-title">Artifacts</h2>
            ${renderArtifactList(job)}
          </section>
        </div>
      `;
      if ((job.status === "queued" || job.status === "running") && !refreshTimer) {
        refreshTimer = window.setInterval(loadStatus, 5000);
      }
      if (job.status === "completed" || job.status === "failed") {
        window.clearInterval(refreshTimer);
        refreshTimer = null;
      }
    } catch (error) {
      output.innerHTML = `<div class="result-box error">${escapeHtml(error.message)}</div>`;
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    window.clearInterval(refreshTimer);
    refreshTimer = null;
    loadStatus();
  });

  if (input.value.trim()) {
    loadStatus();
  }
}

async function initArtifactsPage() {
  renderNav("artifacts");
  const form = byId("artifact-form");
  const input = byId("artifact-job-id");
  const output = byId("artifact-output");
  const previewTitle = byId("artifact-preview-title");
  const previewBody = byId("artifact-preview-body");
  const params = new URLSearchParams(window.location.search);
  if (params.get("id")) {
    input.value = params.get("id");
  }

  async function loadArtifacts() {
    if (!input.value.trim()) return;
    output.innerHTML = `<div class="empty-box">Loading artifacts…</div>`;
    previewTitle.textContent = "Preview";
    previewBody.textContent = "Choose a text or JSON artifact to inspect it here.";
    try {
      const job = await getJson(`/jobs/${encodeURIComponent(input.value.trim())}/artifacts`);
      output.innerHTML = renderArtifactList(job);
      output.querySelectorAll(".artifact-preview").forEach((button) => {
        button.addEventListener("click", async () => {
          previewTitle.textContent = button.dataset.name;
          previewBody.textContent = "Loading preview…";
          try {
            const response = await fetch(button.dataset.url);
            const text = await response.text();
            previewBody.textContent = text;
          } catch (error) {
            previewBody.textContent = error.message;
          }
        });
      });
    } catch (error) {
      output.innerHTML = `<div class="result-box error">${escapeHtml(error.message)}</div>`;
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    loadArtifacts();
  });

  if (input.value.trim()) {
    loadArtifacts();
  }
}

async function initHelpPage() {
  renderNav("help");
  const info = await getJson("/form-options");
  byId("help-runtime").innerHTML = `
    <div class="guide-list">
      <article class="guide-item"><strong>Retention window</strong><div>${escapeHtml(String(info.retention_hours))} hours</div></article>
      <article class="guide-item"><strong>OpenAI transcript summary</strong><div>${info.openai_summary_available ? "Ready once you choose the openai summarizer." : "Server-side OpenAI settings are missing."}</div></article>
      <article class="guide-item"><strong>Available launch fields</strong><div>${info.fields.length} public pipeline parameters</div></article>
    </div>
  `;
}

const page = document.body.dataset.page;
if (page === "upload") initUploadPage();
if (page === "status") initStatusPage();
if (page === "artifacts") initArtifactsPage();
if (page === "help") initHelpPage();
