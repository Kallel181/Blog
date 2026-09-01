document.addEventListener("DOMContentLoaded", () => {
  const article = document.querySelector(".post-body");
  const tocContainer = document.getElementById("toc");

  if (!article || !tocContainer) return;

  const headings = article.querySelectorAll("h2, h3");

  if (headings.length === 0) {
    const sidebar = document.querySelector(".toc-sidebar");
    if (sidebar) sidebar.style.display = "none";
    return;
  }

  const ul = document.createElement("ul");

  headings.forEach((heading, index) => {
    // Garante um ID para navegação por âncora
    if (!heading.id) {
      heading.id = `heading-${index}`;
    }

    const li = document.createElement("li");
    li.className = heading.tagName.toLowerCase() === "h3" ? "toc-h3" : "toc-h2";

    const a = document.createElement("a");
    a.href = `#${heading.id}`;
    a.textContent = heading.textContent;

    li.appendChild(a);
    ul.appendChild(li);
  });

  tocContainer.appendChild(ul);
});