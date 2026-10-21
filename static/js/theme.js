const themeButton = document.getElementById("theme-toggle");

function updateThemeButton() {
  if (!themeButton) return;

  const isDark = document.documentElement.dataset.theme === "dark";

  const icon = themeButton.querySelector(".theme-toggle-icon");
  const label = themeButton.querySelector(".theme-toggle-label");

  if (icon) {
    icon.textContent = isDark ? "☀" : "☾";
  }

  if (label) {
    label.textContent = isDark ? "Modo claro" : "Modo oscuro";
  }

  themeButton.setAttribute("aria-pressed", String(isDark));
  themeButton.setAttribute(
    "aria-label",
    isDark ? "Activar modo claro" : "Activar modo oscuro",
  );
}

themeButton?.addEventListener("click", () => {
  const currentTheme = document.documentElement.dataset.theme;
  const newTheme = currentTheme === "dark" ? "light" : "dark";

  document.documentElement.dataset.theme = newTheme;
  localStorage.setItem("inventory-theme", newTheme);

  updateThemeButton();
});

updateThemeButton();
