function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? match[2] : null;
}
const csrftoken = getCookie("csrftoken");

// --- Kanban drag & drop ---
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card[draggable=true]");
  const columns = document.querySelectorAll(".column-body");

  cards.forEach((card) => {
    card.addEventListener("dragstart", (e) => {
      e.dataTransfer.setData("text/plain", card.dataset.taskId);
      card.classList.add("dragging");
    });
    card.addEventListener("dragend", () => card.classList.remove("dragging"));
  });

  columns.forEach((col) => {
    col.addEventListener("dragover", (e) => e.preventDefault());
    col.addEventListener("drop", async (e) => {
      e.preventDefault();
      const taskId = e.dataTransfer.getData("text/plain");
      const newStatus = col.dataset.status;
      const card = document.querySelector(`.card[data-task-id="${taskId}"]`);
      if (card) col.appendChild(card);

      await fetch(`/tasks/${taskId}/status/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        body: JSON.stringify({ status: newStatus }),
      });
    });
  });

  // --- AI summary preview on the task form ---
  const summarizeBtn = document.getElementById("summarize-btn");
  if (summarizeBtn) {
    summarizeBtn.addEventListener("click", async () => {
      const notesField = document.getElementById("id_meeting_notes");
      const preview = document.getElementById("summary-preview");
      if (!notesField.value.trim()) return;

      summarizeBtn.textContent = "Summarizing...";
      summarizeBtn.disabled = true;

      try {
        const res = await fetch("/api/summarize/", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
          body: JSON.stringify({ notes: notesField.value }),
        });
        const data = await res.json();
        preview.style.display = "block";
        preview.textContent = data.summary || data.error;
      } catch (err) {
        preview.style.display = "block";
        preview.textContent = "Could not generate summary.";
      } finally {
        summarizeBtn.textContent = "✨ Preview AI Summary";
        summarizeBtn.disabled = false;
      }
    });
  }
});
