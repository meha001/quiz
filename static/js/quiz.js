// Логика игровой страницы: показ вопросов, отправка ответов, защита от переключений
document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("quiz-root");
  if (!root) return;

  const sessionId = Number(root.getAttribute("data-session-id"));
  const progressEl = document.getElementById("quiz-progress");
  const questionTextEl = document.getElementById("quiz-question-text");
  const optionsEl = document.getElementById("quiz-options");
  const timerEl = document.getElementById("quiz-timer");
  const statusEl = document.getElementById("quiz-status");
  const nextBtn = document.getElementById("next-btn");

  let quizDataRaw = sessionStorage.getItem(`quiz_session_${sessionId}`);
  if (!quizDataRaw) {
    alert("Данные викторины не найдены. Начните игру заново.");
    window.location.href = "/player";
    return;
  }
  const quizData = JSON.parse(quizDataRaw);
  const questions = quizData.questions || [];
  const totalQuestions = quizData.total_questions || questions.length;

  let currentIndex = 0;
  let canAnswer = true;
  let answered = false;
  let timerId = null;
  let timeLeft = 0;
  let questionStartTime = 0;
  let tabSwitchesLocal = 0;
  let failedLocal = false;

  function startTimer(limit) {
    clearInterval(timerId);
    timeLeft = limit;
    questionStartTime = performance.now();
    timerEl.textContent = `Время на ответ: ${timeLeft} сек.`;
    timerId = setInterval(() => {
      timeLeft -= 1;
      if (timeLeft <= 0) {
        clearInterval(timerId);
        timerEl.textContent = "Время вышло!";
        if (!answered) {
          canAnswer = false;
          statusEl.textContent = "Время на ответ истекло.";
          nextBtn.disabled = false;
        }
      } else {
        timerEl.textContent = `Время на ответ: ${timeLeft} сек.`;
      }
    }, 1000);
  }

  function renderQuestion() {
    if (currentIndex >= questions.length) {
      finishGame();
      return;
    }

    const q = questions[currentIndex];
    if (progressEl) {
      progressEl.textContent = `Вопрос ${currentIndex + 1} из ${totalQuestions}`;
    }
    questionTextEl.textContent = q.text;
    optionsEl.innerHTML = "";
    statusEl.textContent = "";
    answered = false;
    canAnswer = true;
    nextBtn.disabled = true;

    (q.options || []).forEach((opt, idx) => {
      const btn = document.createElement("button");
      btn.className = "btn btn--secondary";
      btn.textContent = opt;
      btn.dataset.index = String(idx);
      btn.addEventListener("click", () => onAnswerClick(btn, q));
      optionsEl.appendChild(btn);
    });

    startTimer(q.time_limit || 30);
  }

  function onAnswerClick(button, question) {
    if (!canAnswer) return;
    canAnswer = false;
    answered = true;
    clearInterval(timerId);

    const chosenIndex = Number(button.dataset.index);
    const elapsedMs = performance.now() - questionStartTime;
    const elapsedSec = elapsedMs / 1000;

    fetch(`/game/${sessionId}/answer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question_id: question.id,
        chosen_index: chosenIndex,
        time_spent: elapsedSec,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        const correct = data.correct;
        const children = Array.from(optionsEl.children);
        children.forEach((btnEl, idx) => {
          if (!(btnEl instanceof HTMLButtonElement)) return;
          btnEl.disabled = true;
          if (idx === chosenIndex) {
            btnEl.style.borderColor = correct ? "#22c55e" : "#ef4444";
          }
        });
        statusEl.textContent = correct
          ? "Правильно!"
          : "Неправильно. Правильный ответ подсвечен зелёным при серверной проверке.";
        nextBtn.disabled = false;
      })
      .catch(() => {
        statusEl.textContent = "Ошибка отправки ответа.";
        nextBtn.disabled = false;
      });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentIndex += 1;
      renderQuestion();
    });
  }

  function finishGame() {
    clearInterval(timerId);
    fetch(`/game/${sessionId}/finish`, {
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        sessionStorage.removeItem(`quiz_session_${sessionId}`);
        const params = new URLSearchParams({
          correct: String(data.correct_count),
          total: String(data.total_questions),
          failed: String(data.failed),
        });
        window.location.href = `/results/${sessionId}?${params.toString()}`;
      })
      .catch(() => {
        alert("Ошибка завершения игры.");
        window.location.href = "/player";
      });
  }

  // Отслеживаем переключения вкладок
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      tabSwitchesLocal += 1;
      fetch(`/game/${sessionId}/tab-switch`, {
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.failed) {
            failedLocal = true;
            statusEl.textContent =
              "Слишком много переключений вкладок. Игра будет помечена как проваленная.";
          } else if (tabSwitchesLocal >= 2) {
            statusEl.textContent =
              "Вы несколько раз переключали вкладки. Ещё немного — и игра будет провалена.";
          }
        })
        .catch(() => {
          // игнорируем ошибки
        });
    }
  });

  renderQuestion();
});

