document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const errorMsg = document.getElementById("error-msg");
  errorMsg.textContent = "";

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  try {
    const response = await fetch(`${API_BASE_URL}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || "Login yoki parol xato");
    }

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token);

    if (data.user.role === "admin") {
      window.location.href = "admin/orders.html";
    } else {
      window.location.href = "index.html";
    }
  } catch (err) {
    errorMsg.textContent = err.message;
  }
});