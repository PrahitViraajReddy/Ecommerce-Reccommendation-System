document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("assistant-form");
  const input = document.getElementById("assistant-message");
  const output = document.getElementById("assistant-answer");
  if (!form || !input || !output) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) { input.focus(); return; }
    const button = form.querySelector("button");
    button.disabled = true; button.textContent = "Thinking…";
    output.textContent = "Finding a helpful answer…";
    try {
      const response = await fetch("/assistant/", {method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":getCookie("csrftoken"),"X-Requested-With":"XMLHttpRequest"},body:JSON.stringify({message})});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Request failed");
      output.textContent = data.answer || "No answer returned.";
    } catch (error) { output.textContent = error.message || "The assistant is temporarily unavailable."; }
    finally { button.disabled = false; button.textContent = "Ask AI ↗"; }
  });
});
function getCookie(name) {
  const match = document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith(name + "="));
  return match ? decodeURIComponent(match.slice(name.length + 1)) : "";
}
