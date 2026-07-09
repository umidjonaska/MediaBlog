function isLoggedIn() {
  return !!getToken();
}

function logout() {
  clearTokens();
  window.location.href = "/login.html";
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "/login.html";
  }
}

async function requireAdmin() {
  try {
    const me = await apiFetch("/me");
    if (me.role !== "admin") {
      alert("Bu sahifaga faqat adminlar kira oladi.");
      window.location.href = "/index.html";
    }
    return me;
  } catch {
    window.location.href = "/login.html";
  }
}