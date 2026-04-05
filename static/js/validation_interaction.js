document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const dateInput = document.getElementById("interaction-date");
  const descriptionInput = document.getElementById("interaction-description");
  const errorBox = document.getElementById("form-errors");

  form.addEventListener("submit", (e) => {
    console.log("APPELLLE");
    errorBox.innerHTML = "";
    const errors = [];


    if (!dateInput.value) {
      errors.push("La date de l’interaction est obligatoire.");
    }

    const description = descriptionInput.value.trim();
    if (!description) {
      errors.push("La description est obligatoire.");
    } 

    if (dateInput.value) {
      const selectedDate = new Date(dateInput.value);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (selectedDate > today) {
        errors.push("La date ne peut pas être dans le futur.");
      }
    }

    if (errors.length > 0) {
      e.preventDefault();
      errors.forEach(msg => {
        const p = document.createElement("p");
        p.textContent = msg;
        errorBox.appendChild(p);
      });
    }
  });
});

