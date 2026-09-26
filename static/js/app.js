(() => {
  const dlg = document.getElementById("confirm");
  const form = document.getElementById("confirm-form");
  const text = document.getElementById("confirm-text");

  // O'chirish tugmasi bosilsa, tasdiqlash oynasi ochiladi
  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-confirm-url]");
    if (opener && dlg && dlg.showModal) {
      e.preventDefault();
      form.action = opener.dataset.confirmUrl;
      text.textContent = opener.dataset.confirmText || "";
      dlg.showModal();
      return;
    }
    // "Yo'q" tugmasi yoki oyna tashqarisiga bosilsa yopiladi
    if (dlg && (e.target === dlg || e.target.closest("[data-close]"))) dlg.close();
  });

  // Tanlangan rasmni darhol ko'rsatadi
  document.addEventListener("change", (e) => {
    const input = e.target;
    if (input.type !== "file" || !input.files || !input.files[0]) return;
    let img = input.parentElement.querySelector(".preview");
    if (!img) {
      img = document.createElement("img");
      img.className = "preview";
      img.alt = "";
      input.after(img);
    }
    img.src = URL.createObjectURL(input.files[0]);
  });

  // Xabarlar 5 soniyadan so'ng yo'qoladi
  setTimeout(() => document.querySelectorAll(".toast").forEach((t) => t.remove()), 5200);
})();
