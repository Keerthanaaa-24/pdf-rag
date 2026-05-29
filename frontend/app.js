const API_BASE = "http://127.0.0.1:8000";

const dropZone = document.getElementById("dropZone");
const browseBtn = document.getElementById("browseBtn");
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");

const askBtn = document.getElementById("askBtn");
const questionInput = document.getElementById("questionInput");

const chatBox = document.getElementById("chatBox");

const loading = document.getElementById("loading");


// -----------------------------
// Drag & Drop
// -----------------------------
browseBtn.addEventListener("click", () => {
  fileInput.click();
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();

  dropZone.classList.remove("dragover");

  const file = e.dataTransfer.files[0];

  if (file) {
    uploadPDF(file);
  }
});

fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];

  if (file) {
    uploadPDF(file);
  }
});


// -----------------------------
// Upload PDF
// -----------------------------
async function uploadPDF(file) {

  if (!file.name.endsWith(".pdf")) {
    uploadStatus.innerHTML = `<span class="error">Please upload a PDF file.</span>`;
    return;
  }

  uploadStatus.innerHTML = "Uploading PDF...";

  disableUI(true);

  const formData = new FormData();

  formData.append("file", file);

  try {

    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload failed");
    }

    uploadStatus.innerHTML = `
      ✅ Uploaded:
      <strong>${data.filename}</strong>
      (${data.chunks} chunks indexed)
    `;

  } catch (error) {

    uploadStatus.innerHTML = `
      <span class="error">
        ${error.message}
      </span>
    `;

  } finally {

    disableUI(false);
  }
}


// -----------------------------
// Ask Question
// -----------------------------
askBtn.addEventListener("click", askQuestion);

questionInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    askQuestion();
  }
});


async function askQuestion() {

  const question = questionInput.value.trim();

  if (!question) return;

  addMessage(question, "user");

  questionInput.value = "";

  loading.classList.remove("hidden");

  disableUI(true);

  try {

    const response = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to get answer");
    }

    addMessage(data.answer, "ai");

  } catch (error) {

    addMessage(`Error: ${error.message}`, "ai");

  } finally {

    loading.classList.add("hidden");

    disableUI(false);
  }
}


// -----------------------------
// Chat Messages
// -----------------------------
function addMessage(text, sender) {

  const messageDiv = document.createElement("div");

  messageDiv.classList.add("message");

  if (sender === "user") {
    messageDiv.classList.add("user-message");
  } else {
    messageDiv.classList.add("ai-message");
  }

  messageDiv.textContent = text;

  chatBox.appendChild(messageDiv);

  chatBox.scrollTop = chatBox.scrollHeight;
}


// -----------------------------
// Disable UI During Requests
// -----------------------------
function disableUI(disabled) {

  askBtn.disabled = disabled;

  questionInput.disabled = disabled;

  browseBtn.disabled = disabled;
}