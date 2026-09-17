/* Student Register — talks to the Django REST API using fetch. */

const API_ROOT = "http://127.0.0.1:8000/api";
const STUDENTS_URL = `${API_ROOT}/students/`;

const form = document.getElementById("student-form");
const panel = form.closest(".panel");
const formHeading = document.getElementById("form-heading");
const idField = document.getElementById("student-id");
const submitButton = document.getElementById("submit-button");
const cancelButton = document.getElementById("cancel-button");
const rows = document.getElementById("student-rows");
const stateMessage = document.getElementById("state-message");
const summary = document.getElementById("summary");
const searchInput = document.getElementById("search");
const departmentFilter = document.getElementById("filter-department");
const toast = document.getElementById("toast");

const FIELDS = [
  "roll_number",
  "full_name",
  "email",
  "phone",
  "department",
  "year_of_study",
  "cgpa",
];

/* ------------------------------------------------------------ helpers */

let toastTimer;
function notify(message, isError = false) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function clearErrors() {
  document.querySelectorAll(".error").forEach((el) => (el.textContent = ""));
  document
    .querySelectorAll("input, select")
    .forEach((el) => el.classList.remove("invalid"));
}

function showFieldError(name, message) {
  const slot = document.querySelector(`[data-error-for="${name}"]`);
  const input = document.getElementById(name);
  if (slot) slot.textContent = message;
  if (input) input.classList.add("invalid");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

/* -------------------------------------------------- client validation */

function validateClientSide(data) {
  const errors = {};

  if (!data.roll_number.trim()) {
    errors.roll_number = "Roll number is required.";
  } else if (!/^[A-Za-z0-9/-]+$/.test(data.roll_number.trim())) {
    errors.roll_number = "Use letters, digits, - and / only.";
  }

  if (!data.full_name.trim()) {
    errors.full_name = "Full name is required.";
  } else if (data.full_name.trim().length < 3) {
    errors.full_name = "Use at least 3 characters.";
  }

  if (!data.email.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email.trim())) {
    errors.email = "Enter a valid email address.";
  }

  if (data.phone && !/^\d{10}$/.test(data.phone.trim())) {
    errors.phone = "Enter 10 digits, or leave this blank.";
  }

  if (!data.department) errors.department = "Choose a department.";
  if (!data.year_of_study) errors.year_of_study = "Choose a year.";

  if (data.cgpa === "") {
    errors.cgpa = "CGPA is required.";
  } else if (Number(data.cgpa) < 0 || Number(data.cgpa) > 10) {
    errors.cgpa = "CGPA must be between 0 and 10.";
  }

  return errors;
}

/* ----------------------------------------------------------- read all */

async function loadStudents() {
  const params = new URLSearchParams();
  if (searchInput.value.trim()) params.set("search", searchInput.value.trim());
  if (departmentFilter.value) params.set("department", departmentFilter.value);

  stateMessage.textContent = "Loading records…";
  rows.innerHTML = "";

  try {
    const response = await fetch(`${STUDENTS_URL}?${params}`);
    if (!response.ok) throw new Error(`Server responded with ${response.status}`);
    const students = await response.json();
    renderRows(students);
  } catch (error) {
    stateMessage.textContent =
      "Cannot reach the API. Start the Django server on port 8000 and reload.";
    summary.textContent = "The register is offline.";
  }
}

function renderRows(students) {
  if (!students.length) {
    stateMessage.textContent = searchInput.value || departmentFilter.value
      ? "No student matches this search."
      : "No students yet. Add the first record using the form.";
    updateSummary(0);
    return;
  }

  stateMessage.textContent = "";
  rows.innerHTML = students
    .map(
      (s) => `
      <tr>
        <td class="roll">${escapeHtml(s.roll_number)}</td>
        <td>
          ${escapeHtml(s.full_name)}
          <span class="email">${escapeHtml(s.email)}</span>
        </td>
        <td>${escapeHtml(s.department)}</td>
        <td class="num">${escapeHtml(s.year_of_study)}</td>
        <td class="num">${escapeHtml(s.cgpa)}</td>
        <td>
          <div class="row-actions">
            <button type="button" class="link-button" data-edit="${s.id}">Edit</button>
            <button type="button" class="link-button delete" data-delete="${s.id}" data-roll="${escapeHtml(s.roll_number)}">Delete</button>
          </div>
        </td>
      </tr>`
    )
    .join("");

  updateSummary(students.length);
}

async function updateSummary(visibleCount) {
  try {
    const response = await fetch(`${API_ROOT}/stats/`);
    const stats = await response.json();
    if (stats.total_students === 0) {
      summary.textContent = "The register is empty.";
      return;
    }
    const average = stats.average_cgpa ?? "—";
    summary.innerHTML =
      `<strong>${stats.total_students}</strong> student${stats.total_students === 1 ? "" : "s"} on record, ` +
      `average CGPA <strong>${average}</strong>. Showing ${visibleCount}.`;
  } catch {
    summary.textContent = `Showing ${visibleCount} record(s).`;
  }
}

/* ------------------------------------------------------ create/update */

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearErrors();

  const data = Object.fromEntries(FIELDS.map((f) => [f, document.getElementById(f).value]));
  const errors = validateClientSide(data);

  if (Object.keys(errors).length) {
    Object.entries(errors).forEach(([field, message]) => showFieldError(field, message));
    notify("Fix the highlighted fields before saving.", true);
    return;
  }

  const editingId = idField.value;
  const url = editingId ? `${STUDENTS_URL}${editingId}/` : STUDENTS_URL;
  const method = editingId ? "PUT" : "POST";

  submitButton.disabled = true;
  submitButton.textContent = "Saving…";

  try {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const payload = await response.json();

    if (!response.ok) {
      const fieldErrors = payload.errors || {};
      Object.entries(fieldErrors).forEach(([field, messages]) => {
        showFieldError(field, Array.isArray(messages) ? messages[0] : messages);
      });
      notify(payload.message || "The server rejected this record.", true);
      return;
    }

    notify(editingId ? `Updated ${payload.roll_number}.` : `Added ${payload.roll_number}.`);
    resetForm();
    loadStudents();
  } catch (error) {
    notify("Cannot reach the API. Is the Django server running?", true);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = idField.value ? "Update student" : "Save student";
  }
});

/* --------------------------------------------------------- edit/delete */

rows.addEventListener("click", async (event) => {
  const editId = event.target.dataset.edit;
  const deleteId = event.target.dataset.delete;

  if (editId) await startEditing(editId);
  if (deleteId) await deleteStudent(deleteId, event.target.dataset.roll);
});

async function startEditing(id) {
  try {
    const response = await fetch(`${STUDENTS_URL}${id}/`);
    if (!response.ok) throw new Error("Record not found");
    const student = await response.json();

    clearErrors();
    FIELDS.forEach((f) => (document.getElementById(f).value = student[f] ?? ""));
    idField.value = student.id;

    formHeading.textContent = `Edit ${student.roll_number}`;
    submitButton.textContent = "Update student";
    cancelButton.classList.remove("hidden");
    panel.classList.add("is-editing");
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch {
    notify("That record no longer exists. Refreshing the list.", true);
    loadStudents();
  }
}

async function deleteStudent(id, roll) {
  if (!confirm(`Delete student ${roll}? This cannot be undone.`)) return;

  try {
    const response = await fetch(`${STUDENTS_URL}${id}/`, { method: "DELETE" });
    if (!response.ok) {
      notify("That record could not be deleted. It may already be gone.", true);
    } else {
      notify(`Deleted ${roll}.`);
      if (idField.value === String(id)) resetForm();
    }
    loadStudents();
  } catch {
    notify("Cannot reach the API. Is the Django server running?", true);
  }
}

function resetForm() {
  form.reset();
  idField.value = "";
  clearErrors();
  formHeading.textContent = "Add a student";
  submitButton.textContent = "Save student";
  cancelButton.classList.add("hidden");
  panel.classList.remove("is-editing");
}

cancelButton.addEventListener("click", resetForm);

/* ------------------------------------------------------ search/filter */

let searchTimer;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadStudents, 250);
});
departmentFilter.addEventListener("change", loadStudents);

loadStudents();
