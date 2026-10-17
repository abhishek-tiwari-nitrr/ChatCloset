// Orders page: everything this browser has ordered, newest first.
import { api } from '../api.js';
import { escapeHtml, formatPrice } from '../ui.js';

export async function renderOrders() {
  const orders = await api.listOrders();
  document.getElementById('app').innerHTML = `
    <h1 class="page-title">Your orders</h1>
    ${orders.length ? orders.map(orderCard).join('') : '<div class="empty-state"><p>📦</p><h2>No orders yet</h2><a href="#/" class="btn">Start shopping</a></div>'}`;
}

const orderCard = (order) => `
  <article class="panel order">
    <header class="order-head">
      <strong>Order #${escapeHtml(order.id.slice(-6).toUpperCase())}</strong>
      <span class="muted">${new Date(order.created_at).toLocaleString()}</span>
      <span class="badge">${escapeHtml(order.status)}</span>
    </header>
    <ul class="order-lines">
      ${order.items.map((item) => `
        <li><span>${item.quantity} × ${escapeHtml(item.name)} (${escapeHtml(item.size)})</span><span>${formatPrice(item.price * item.quantity)}</span></li>`).join('')}
    </ul>
    <p class="order-total">Total ${formatPrice(order.total)}</p>
  </article>`;
