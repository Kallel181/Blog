document.addEventListener("DOMContentLoaded", () => {
  const article = document.querySelector(".post-body");
  const tocContainer = document.getElementById("toc");

  if (!article || !tocContainer) return;

  // Adicionado h1 na busca
  const headings = article.querySelectorAll("h1, h2, h3, h4");

  if (headings.length === 0) {
    const sidebar = document.querySelector(".toc-sidebar");
    if (sidebar) sidebar.style.display = "none";
    return;
  }

  const ul = document.createElement("ul");

  headings.forEach((heading, index) => {
    if (!heading.id) {
      heading.id = `heading-${index}`;
    }

    const li = document.createElement("li");
    const tag = heading.tagName.toLowerCase();
    
    // Define a classe CSS correspondente para cada nível de título
    li.className = `toc-${tag}`;

    const a = document.createElement("a");
    a.href = `#${heading.id}`;
    a.textContent = heading.textContent;

    li.appendChild(a);
    ul.appendChild(li);
  });

  tocContainer.appendChild(ul);
});