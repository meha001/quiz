const API_BASE_URL = "http://127.0.0.1:8000";

const output = document.getElementById("output");
const loading = document.getElementById("loading");
const healthBtn = document.getElementById("healthBtn");
const itemsBtn = document.getElementById("itemsBtn");
const echoForm = document.getElementById("echoForm");
const userForm = document.getElementById("userForm");
const loadUsersBtn = document.getElementById("loadUsersBtn");
const usersList = document.getElementById("usersList");

function renderJson(data) {
  output.textContent = JSON.stringify(data, null, 2);
}

function setLoading(isLoading) {
  loading.classList.toggle("hidden", !isLoading);
}

function getErrorMessage(error, fallback = "Не удалось выполнить запрос") {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  return fallback;
}

async function requestJson(path, options = {}) {
  setLoading(true);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const message =
        data?.detail || `Ошибка запроса: ${response.status} ${response.statusText}`;
      throw new Error(message);
    }

    renderJson(data);
    return data;
  } catch (error) {
    renderJson({
      error: getErrorMessage(error, "Сетевая ошибка"),
      hint: "Проверьте, запущен ли backend на http://127.0.0.1:8000",
    });
    return null;
  } finally {
    setLoading(false);
  }
}

healthBtn.addEventListener("click", () => {
  requestJson("/api/health");
});

itemsBtn.addEventListener("click", () => {
  requestJson("/api/items");
});

echoForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(echoForm);
  const payload = {
    message: String(formData.get("message") || ""),
    // Отправляем ISO-дату, чтобы пройти валидацию схемы на бэкенде
    timestamp: new Date().toISOString(),
  };

  requestJson("/api/echo", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
});

function renderUsers(users) {
  usersList.innerHTML = "";

  if (!Array.isArray(users) || users.length === 0) {
    const empty = document.createElement("li");
    empty.className = "user-meta";
    empty.textContent = "Пользователи пока не добавлены.";
    usersList.append(empty);
    return;
  }

  users.forEach((user) => {
    const row = document.createElement("li");
    row.className = "user-row";

    const meta = document.createElement("span");
    meta.className = "user-meta";
    meta.textContent = `#${user.id} ${user.name} (${user.email})`;

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "delete-btn";
    removeBtn.textContent = "Удалить";
    removeBtn.addEventListener("click", async () => {
      const result = await requestJson(`/api/users/${user.id}`, { method: "DELETE" });
      if (result) {
        loadUsers();
      }
    });

    row.append(meta, removeBtn);
    usersList.append(row);
  });
}

async function loadUsers() {
  const users = await requestJson("/api/users");
  if (users) {
    renderUsers(users);
  }
}

userForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(userForm);

  const payload = {
    name: String(formData.get("userName") || "").trim(),
    email: String(formData.get("userEmail") || "").trim(),
  };

  const created = await requestJson("/api/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (created) {
    userForm.reset();
    loadUsers();
  }
});

loadUsersBtn.addEventListener("click", () => {
  loadUsers();
});

loadUsers();
