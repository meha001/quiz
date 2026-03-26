// Логика страницы игрока: выбор викторины, анти-спам по времени и старт игры
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("player-form");
  const creatorSelect = document.getElementById("creator-select");
  const highscoresContainer = document.getElementById("highscores-container");
  if (!form) return;

  // Подгружаем список викторин (создателей)
  fetch("/stats/creators")
    .then((res) => res.json())
    .then((creators) => {
      if (!Array.isArray(creators)) return;
      creators.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = `${c.username} — ⭐ ${c.reputation} (игроков: ${c.players_passed})`;
        creatorSelect.appendChild(opt);
      });
    })
    .catch(() => {
      // тихо игнорируем
    });

  creatorSelect.addEventListener("change", () => {
    const id = creatorSelect.value;
    if (!id) {
      highscoresContainer.innerHTML = '<p class="muted">Выберите викторину, чтобы увидеть рекорды.</p>';
      return;
    }
    fetch(`/stats/creators/${id}/highscores?period=all&limit=10`)
      .then((res) => res.json())
      .then((items) => {
        if (!Array.isArray(items) || items.length === 0) {
          highscoresContainer.innerHTML = '<p class="muted">Пока нет рекордов.</p>';
          return;
        }
        const rows = items
          .map(
            (h, idx) =>
              `<tr><td>${idx + 1}</td><td>${h.player_name}</td><td>${h.score}</td></tr>`,
          )
          .join("");
        highscoresContainer.innerHTML = `
          <table class="table">
            <thead><tr><th>#</th><th>Игрок</th><th>Баллы</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        `;
      })
      .catch(() => {
        highscoresContainer.innerHTML = '<p class="muted">Ошибка загрузки рекордов.</p>';
      });
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const playerName = formData.get("player_name");
    const creatorId = formData.get("creator_id");

    if (!playerName || !creatorId) {
      alert("Введите имя и выберите викторину.");
      return;
    }

    // Ограничение: не чаще одного раза в 10 минут
    const key = `last_play_${creatorId}`;
    const now = Date.now();
    const last = localStorage.getItem(key);
    if (last && now - Number(last) < 10 * 60 * 1000) {
      alert("Вы уже играли эту викторину недавно. Подождите немного прежде чем играть снова.");
      return;
    }

    const captchaAnswer = Number(prompt("Небольшая проверка: сколько будет 2 + 2 ?"));
    if (!Number.isFinite(captchaAnswer)) {
      alert("Введите число.");
      return;
    }

    fetch("/game/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        player_name: playerName,
        creator_id: Number(creatorId),
        captcha_answer: captchaAnswer,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          const msg = data.detail || "Ошибка старта игры";
          throw new Error(msg);
        }
        return res.json();
      })
      .then((data) => {
        localStorage.setItem(key, String(now));
        // сохраняем вопросы в sessionStorage для страницы игры
        sessionStorage.setItem(
          `quiz_session_${data.session_id}`,
          JSON.stringify({
            questions: data.questions,
            total_questions: data.total_questions,
          }),
        );
        window.location.href = `/game/${data.session_id}`;
      })
      .catch((err) => {
        alert(err.message || "Ошибка старта игры");
      });
  });
});
