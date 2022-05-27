document.addEventListener(
  "DOMContentLoaded",
  function () {
    var a = document.createElement("a");
    a.textContent = "Get Started";
    a.href = "https://pyshiny.netlify.app/";
    a.style =
      "float:right; color:#5a5a5a; margin-right:5px; margin-top:5px; font-weight:600; text-decoration:none;";
    a.setAttribute("data-toggle", "tooltip");
    a.setAttribute("data-placement", "bottom");
    a.setAttribute("data-original-title", "Learn Shiny for Python");

    var nav = document.querySelector(".topbar-main");
    if (!nav) {
      nav = document.querySelector(".header-article-main .header-article__right");
    }
    if (nav) nav.appendChild(a);
  },
  false
);
