// Переключение вкладок, CRUD вопросов, настройки и статистика создателя
document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll(".tabs__item");
  const tabs = document.querySelectorAll(".tab");
  const logoutBtn = document.getElementById("logout-btn");
  const questionForm = document.getElementById("question-form");
  const questionsContainer = document.getElementById("questions-table-container");
  const statsSummary = document.getElementById("stats-summary");
  const ratingBlock = document.getElementById("rating-block");
  const settingsForm = document.getElementById("settings-form");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabName = btn.getAttribute("data-tab");
      if (!tabName) return;

      tabButtons.forEach((b) => b.classList.remove("tabs__item--active"));
      tabs.forEach((t) => t.classList.remove("tab--active"));

      btn.classList.add("tabs__item--active");
      const activeTab = document.getElementById(`tab-${tabName}`);
      if (activeTab) activeTab.classList.add("tab--active");
    });
  });

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      fetch("/auth/logout", {
        method: "POST",
      }).finally(() => {
        window.location.href = "/";
      });
    });
  }

  function loadQuestions() {
    if (!questionsContainer) return;
    fetch("/creator/api/questions")
      .then((res) => res.json())
      .then((questions) => {
        if (!Array.isArray(questions) || questions.length === 0) {
          questionsContainer.innerHTML = '<p class="muted">Пока нет ни одного вопроса.</p>';
          return;
        }
        const rows = questions
          .map(
            (q) => `
          <tr data-id="${q.id}">
            <td>${q.id}</td>
            <td>${q.text}</td>
            <td>${q.time_limit}</td>
            <td>${q.correct_index}</td>
            <td>
              <button class="btn btn--ghost btn-sm" data-action="edit">Изменить</button>
              <button class="btn btn--ghost btn-sm" data-action="delete">Удалить</button>
            </td>
          </tr>`,
          )
          .join("");
        questionsContainer.innerHTML = `
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Текст</th>
                <th>Время</th>
                <th>Правильный</th>
                <th></th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        `;

        const tbody = questionsContainer.querySelector("tbody");
        if (!tbody) return;
        tbody.addEventListener("click", (e) => {
          const target = e.target;
          if (!(target instanceof HTMLElement)) return;
          const action = target.dataset.action;
          const tr = target.closest("tr");
          if (!tr) return;
          const id = tr.getAttribute("data-id");
          if (!id) return;
          const q = questions.find((item) => String(item.id) === String(id));
          if (!q) return;

          if (action === "edit") {
            fillQuestionForm(q);
          } else if (action === "delete") {
            if (confirm("Удалить вопрос?")) {
              fetch(`/creator/api/questions/${id}`, { method: "DELETE" }).then(() => {
                loadQuestions();
              });
            }
          }
        });
      })
      .catch(() => {
        questionsContainer.innerHTML = '<p class="muted">Ошибка загрузки вопросов.</p>';
      });
  }

  function fillQuestionForm(q) {
    document.getElementById("q-id").value = q.id;
    document.getElementById("q-text").value = q.text;
    document.getElementById("q-opt1").value = q.option_1;
    document.getElementById("q-opt2").value = q.option_2;
    document.getElementById("q-opt3").value = q.option_3;
    document.getElementById("q-opt4").value = q.option_4;
    document.getElementById("q-correct").value = q.correct_index;
    document.getElementById("q-time").value = q.time_limit;
  }

  if (questionForm) {
    const resetBtn = document.getElementById("q-reset-btn");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        questionForm.reset();
        document.getElementById("q-id").value = "";
      });
    }

    questionForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const id = document.getElementById("q-id").value;

      const payload = {
        text: document.getElementById("q-text").value,
        option_1: document.getElementById("q-opt1").value,
        option_2: document.getElementById("q-opt2").value,
        option_3: document.getElementById("q-opt3").value,
        option_4: document.getElementById("q-opt4").value,
        correct_index: Number(document.getElementById("q-correct").value),
        time_limit: Number(document.getElementById("q-time").value),
      };

      const method = id ? "PUT" : "POST";
      const url = id ? `/creator/api/questions/${id}` : "/creator/api/questions";

      fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Ошибка сохранения вопроса");
          return res.json();
        })
        .then(() => {
          questionForm.reset();
          document.getElementById("q-id").value = "";
          loadQuestions();
        })
        .catch((err) => alert(err.message || "Ошибка сохранения вопроса"));
    });
  }

  function loadSettings() {
    if (!settingsForm) return;
    fetch("/creator/api/settings")
      .then((res) => res.json())
      .then((s) => {
        document.getElementById("s-time").value = s.default_question_time;
        document.getElementById("s-count").value = s.questions_per_game;
        document.getElementById("s-shuffle").value = String(s.shuffle_questions);
      })
      .catch(() => {
        // оставляем значения по умолчанию
      });
  }

  if (settingsForm) {
    settingsForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const payload = {
        default_question_time: Number(document.getElementById("s-time").value),
        questions_per_game: Number(document.getElementById("s-count").value),
        shuffle_questions: document.getElementById("s-shuffle").value === "true",
      };
      fetch("/creator/api/settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Ошибка сохранения настроек");
          return res.json();
        })
        .then(() => alert("Настройки сохранены"))
        .catch((err) => alert(err.message || "Ошибка сохранения настроек"));
    });
  }

  function loadStatsAndRating() {
    fetch("/stats/creator/me/summary")
      .then((res) => res.json())
      .then((s) => {
        if (statsSummary) {
          statsSummary.innerHTML = `
            <p>Всего игроков: <strong>${s.players_passed}</strong></p>
            <p>Средний балл: <strong>${s.avg_score}</strong> / 10</p>
          `;
        }
        if (ratingBlock) {
          ratingBlock.innerHTML = `
            <p>Создатель: <strong>${s.username}</strong></p>
            <p>Репутация: <strong>⭐ ${s.reputation}</strong></p>
            <p>Игроков прошли викторину: <strong>${s.players_passed}</strong></p>
            <p>Средний балл: <strong>${s.avg_score}</strong> / 10</p>
          `;
        }
      })
      .catch(() => {
        if (statsSummary) {
          statsSummary.innerHTML = '<p class="muted">Ошибка загрузки статистики.</p>';
        }
        if (ratingBlock) {
          ratingBlock.innerHTML = '<p class="muted">Ошибка загрузки репутации.</p>';
        }
      });
  }

  loadQuestions();
  loadSettings();
  loadStatsAndRating();
});

