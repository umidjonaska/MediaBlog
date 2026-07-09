let currentCursor = "0";
const PAGE_SIZE = 20;

document.getElementById("logout-link").addEventListener("click", (e) => {
  e.preventDefault();
  logout();
});

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function statusBadgeClass(status) {
  if (status === "yangi") return "status-yangi";
  if (status === "topshirildi") return "status-topshirildi";
  return "status-bekor";
}

function statusLabel(status) {
  const labels = { yangi: "Yangi", topshirildi: "Topshirildi", "bekor qilindi": "Bekor qilindi" };
  return labels[status] || status;
}

async function loadOrders(cursor = "0") {
  const container = document.getElementById("orders-container");

  try {
    const page = await apiFetch(`/order?size=${PAGE_SIZE}&cursor=${cursor}`);

    updateStats(page);
    renderTable(page.data);
    renderPagination(page);
  } catch (err) {
    container.innerHTML = `<p class="error">Xatolik: ${err.message}</p>`;
  }
}

function updateStats(page) {
  document.getElementById("stat-total").textContent = page.count;
  document.getElementById("stat-new").textContent = page.data.filter((o) => o.status === "yangi").length;
  document.getElementById("stat-quantity").textContent = page.data.reduce((sum, o) => sum + o.quantity, 0);
}

function renderTable(orders) {
  const container = document.getElementById("orders-container");

  if (orders.length === 0) {
    container.innerHTML = "<p>Buyurtmalar topilmadi.</p>";
    return;
  }

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Mijoz</th>
          <th>Telefon</th>
          <th>Mahsulot</th>
          <th>Miqdor</th>
          <th>Holat</th>
          <th>Sana</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        ${orders
          .map(
            (o) => `
          <tr>
            <td>${o.id}</td>
            <td>${escapeHtml(o.customer_name)}</td>
            <td>${escapeHtml(o.customer_phone)}</td>
            <td>${escapeHtml(o.product_name)}</td>
            <td>${o.quantity}</td>
            <td><span class="status-badge ${statusBadgeClass(o.status)}">${statusLabel(o.status)}</span></td>
            <td>${new Date(o.created_at).toLocaleDateString("uz-UZ")}</td>
            <td>
              <select onchange="updateOrderStatus(${o.id}, this.value)">
                <option value="">Holatni o'zgartirish</option>
                <option value="yangi">Yangi</option>
                <option value="topshirildi">Topshirildi</option>
                <option value="bekor qilindi">Bekor qilindi</option>
              </select>
              <button class="secondary" onclick="deleteOrder(${o.id})">O'chirish</button>
            </td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function renderPagination(page) {
  const container = document.getElementById("pagination");

  if (!page.next_cursor) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = `<button id="next-page-btn">Keyingi sahifa →</button>`;
  document.getElementById("next-page-btn").addEventListener("click", () => {
    currentCursor = page.next_cursor;
    loadOrders(currentCursor);
  });
}

async function updateOrderStatus(orderId, newStatus) {
  if (!newStatus) return;

  try {
    await apiFetch(`/order/${orderId}`, {
      method: "PUT",
      body: JSON.stringify({ status: newStatus }),
    });
    loadOrders(currentCursor);
  } catch (err) {
    alert(`Xatolik: ${err.message}`);
  }
}

async function deleteOrder(orderId) {
  if (!confirm("Rostdan ham bu buyurtmani o'chirmoqchimisiz?")) return;

  try {
    await apiFetch(`/order/${orderId}`, { method: "DELETE" });
    loadOrders(currentCursor);
  } catch (err) {
    alert(`Xatolik: ${err.message}`);
  }
}

(async function init() {
  await requireAdmin();
  loadOrders();
})();