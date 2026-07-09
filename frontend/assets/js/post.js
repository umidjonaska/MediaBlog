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

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function getPostId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

async function loadPost() {
  const postId = getPostId();
  const container = document.getElementById("post-container");

  if (!postId) {
    container.innerHTML = `<p class="error">Post ID topilmadi.</p>`;
    return;
  }

  try {
    const post = await apiFetch(`/post/${postId}`);

    container.innerHTML = `
      <div class="card">
        <h1>${escapeHtml(post.title)}</h1>
        <p>${escapeHtml(post.content)}</p>
        <p style="margin-top: 12px; color: #999; font-size: 13px;">
          👍 ${post.likes} | ${new Date(post.created_at).toLocaleDateString("uz-UZ")}
        </p>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p class="error">Xatolik: ${err.message}</p>`;
  }
}

async function loadComments() {
  const postId = getPostId();
  const container = document.getElementById("comments-container");

  try {
    const page = await apiFetch(`/comment?size=100&cursor=0`);
    const comments = page.data.filter((c) => c.post_id === Number(postId));

    if (comments.length === 0) {
      container.innerHTML = `<p style="color:#999;">Hozircha kommentlar yo'q.</p>`;
      return;
    }

    container.innerHTML = comments
      .map(
        (c) => `
      <div style="padding: 10px 0; border-bottom: 1px solid #eee;">
        <p>${escapeHtml(c.content)}</p>
        <p style="font-size: 12px; color: #999;">${new Date(c.created_at).toLocaleDateString("uz-UZ")}</p>
      </div>
    `
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<p class="error">Kommentlarni yuklashda xatolik: ${err.message}</p>`;
  }
}

function renderCommentForm() {
  const container = document.getElementById("comment-form-container");

  if (!isLoggedIn()) {
    container.innerHTML = `<p><a href="login.html">Kirib</a>, komment qoldiring.</p>`;
    return;
  }

  container.innerHTML = `
    <form id="comment-form">
      <textarea id="comment-content" placeholder="Komment yozing..." required rows="3"></textarea>
      <button type="submit">Yuborish</button>
      <p class="error" id="comment-error"></p>
    </form>
  `;

  document.getElementById("comment-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const content = document.getElementById("comment-content").value;
    const errorMsg = document.getElementById("comment-error");
    errorMsg.textContent = "";

    try {
      await apiFetch("/comment", {
        method: "POST",
        body: JSON.stringify({ content, post_id: Number(getPostId()) }),
      });
      document.getElementById("comment-content").value = "";
      loadComments();
    } catch (err) {
      errorMsg.textContent = err.message;
    }
  });
}

renderNav();
loadPost();
loadComments();
renderCommentForm();