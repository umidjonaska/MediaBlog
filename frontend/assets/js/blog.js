function renderNav() {
  const nav = document.getElementById("nav-links");

  if (isLoggedIn()) {
    nav.innerHTML = `
      <a href="admin/orders.html">Admin</a>
      <a href="#" id="logout-link">Chiqish</a>
    `;
    document.getElementById("logout-link").addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  } else {
    nav.innerHTML = `<a href="login.html">Kirish</a>`;
  }
}

async function loadPosts() {
  const container = document.getElementById("posts-container");

  try {
    const page = await apiFetch("/post?size=20&cursor=0");

    if (page.data.length === 0) {
      container.innerHTML = "<p>Hozircha postlar yo'q.</p>";
      return;
    }

    container.innerHTML = page.data
      .map(
        (post) => `
      <div class="card">
        <h2><a href="post.html?id=${post.id}">${escapeHtml(post.title)}</a></h2>
        <p>${escapeHtml(post.content.slice(0, 150))}...</p>
      </div>
    `
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<p class="error">Xatolik: ${err.message}</p>`;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

renderNav();
loadPosts();