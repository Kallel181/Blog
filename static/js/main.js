const postsPerPage = 10;
let currentPage = 1;
let allPosts = [];

document.addEventListener("DOMContentLoaded", () => {
  fetch("/static/posts.json")
    .then(res => res.json())
    .then(data => {
      allPosts = data.posts;
      renderPosts();
    });

  document.getElementById("search-input").addEventListener("input", () => {
    currentPage = 1;
    renderPosts();
  });
});

function renderPosts() {
  const search = document.getElementById("search-input").value.toLowerCase();

  const filtered = allPosts.filter(post => {
    return post.name.toLowerCase().includes(search) ||
      post.tags.some(tag => tag.toLowerCase().includes(search));
  });

  const start = (currentPage - 1) * postsPerPage;
  const paginated = filtered.slice(start, start + postsPerPage);

  const postsList = document.getElementById("posts-list");
  postsList.innerHTML = "";

  paginated.forEach(post => {
    const el = document.createElement("a");
    el.href = post.file_location;
    el.className = "post-card";
    el.innerHTML = `
      <img src="${post.icon_location}" alt="${post.name}" class="img_icon">
      <div class="post-info">
        <h3>${post.name}</h3>
        <p>${post.resume}</p>
        <div class="date">${post.date}</div>
        <div class="tags">${post.tags.map(tag => `<span class="tag">${tag}</span>`).join("")}</div>
      </div>
    `;
    postsList.appendChild(el);
  });

  renderPagination(filtered.length);
}

function renderPagination(totalItems) {
  const totalPages = Math.ceil(totalItems / postsPerPage);
  const container = document.getElementById("pagination");
  container.innerHTML = "";

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = "page-button";
    if (i === currentPage) btn.classList.add("active");

    btn.addEventListener("click", () => {
      currentPage = i;
      renderPosts();
    });

    container.appendChild(btn);
  }
}
