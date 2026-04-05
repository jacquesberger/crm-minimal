document.addEventListener("DOMContentLoaded", () => {
  const currentPath = window.location.pathname.replace(/\/$/, "");

  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href").replace(/\/$/, "");

    if (href && currentPath === href) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    } else {
      link.classList.remove("active");
      link.removeAttribute("aria-current");
    }
  });
});
