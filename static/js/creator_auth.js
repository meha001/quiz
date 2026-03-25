// Логика регистрации/входа создателя через API FastAPI
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("creator-login-form");
  const registerBtn = document.getElementById("creator-register-btn");

  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const formData = new FormData(loginForm);
      const payload = {
        username: formData.get("username"),
        password: formData.get("password"),
      };

      fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then(async (res) => {
          if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            const msg = data.detail || "Ошибка входа";
            throw new Error(msg);
          }
          return res.json();
        })
        .then(() => {
          window.location.href = "/creator/dashboard";
        })
        .catch((err) => {
          alert(err.message || "Ошибка входа");
        });
    });
  }

  if (registerBtn) {
    registerBtn.addEventListener("click", () => {
      const loginForm = document.getElementById("creator-login-form");
      if (!loginForm) return;

      const formData = new FormData(loginForm);
      const payload = {
        username: formData.get("username"),
        password: formData.get("password"),
      };

      fetch("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then(async (res) => {
          if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            const msg = data.detail || "Ошибка регистрации";
            throw new Error(msg);
          }
          return res.json();
        })
        .then(() => {
          window.location.href = "/creator/dashboard";
        })
        .catch((err) => {
          alert(err.message || "Ошибка регистрации");
        });
    });
  }
});

