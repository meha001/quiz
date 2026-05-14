// Список викторин на главной (публичный API)
document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("top-quizzes-list");
  if (!root) return;

  root.innerHTML = '<p class="muted">Загрузка списка…</p>';

  fetch("/stats/quizzes")
    .then((res) => {
      if (!res.ok) throw new Error("bad status");
      return res.json();
    })
    .then((quizzes) => {
      if (!Array.isArray(quizzes) || quizzes.length === 0) {
        root.innerHTML =
          '<p class="muted">Пока нет викторин. Зайдите как создатель и добавьте тест с вопросами.</p>';
        return;
      }
      const ul = document.createElement("ul");
      ul.className = "top-quizzes__list";
      quizzes.forEach((q) => {
        const li = document.createElement("li");
        const title = document.createElement("span");
        title.textContent = q.title;
        const link = document.createElement("a");
        link.className = "btn btn--secondary btn-sm";
        link.href = `/player?quiz=${encodeURIComponent(String(q.id))}`;
        link.textContent = "Играть";
        li.appendChild(title);
        li.appendChild(link);
        ul.appendChild(li);
      });
      root.innerHTML = "";
      root.appendChild(ul);
    })
    .catch(() => {
      root.innerHTML =
        '<p class="muted">Не удалось загрузить список. Обновите страницу или откройте раздел «Игрок».</p>';
    });
});
