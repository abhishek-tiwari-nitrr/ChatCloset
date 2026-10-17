// Cart page: lines with quantity steppers, a server-calculated total and the "Place order" button.
import { api } from '../api.js';
import { updateCartCount } from '../components/header.js';
import { escapeHtml, formatPrice, toast } from '../ui.js';

export async function renderCart() {
  const cart = await api.getCart();
  const app = document.getElementById('app');
  updateCartCount(cart.count);
  if (!cart.items.length) {
    app.innerHTML = '<div class="empty-state"><p>🛒</p><h2>Your cart is empty</h2><a href="#/" class="btn">Start shopping</a></div>';
    return;
  }
  app.innerHTML = `
    <h1 class="page-title">Your cart</h1>
    <div class="cart-layout">
      <ul class="cart-list">${cart.items.map(cartLine).join('')}</ul>
      <aside class="panel summary">
        <div class="summary-row"><span>Items</span><span>${cart.count}</span></div>
        <div class="summary-row"><span>Delivery</span><span>Free</span></div>
        <div class="summary-row total"><span>Total</span><span>${formatPrice(cart.total)}</span></div>
        <button id="checkout" class="btn btn-block">Place order</button>
      </aside>
    </div>`;

  app.querySelectorAll('[data-qty]').forEach((button) => {
    button.addEventListener('click', async () => {
      const { id, size, qty } = button.dataset;
      try {
        await api.setQuantity(id, size, Number(qty));
        await renderCart();
      } catch (error) {
        toast(error.message, 'error');
      }
    });
  });

  document.getElementById('checkout').addEventListener('click', async (event) => {
    event.target.disabled = true;
    try {
      const order = await api.checkout();
      updateCartCount(0);
      toast(`Order placed! Total ${formatPrice(order.total)}`, 'success');
      location.hash = '#/orders';
    } catch (error) {
      toast(error.message, 'error');
      event.target.disabled = false;
    }
  });
}

function cartLine(item) {
  const keys = `data-id="${escapeHtml(item.product_id)}" data-size="${escapeHtml(item.size)}"`;
  return `
    <li class="panel cart-line">
      <img src="${escapeHtml(item.image)}" alt="" />
      <div class="cart-line-info">
        <a href="#/product/${escapeHtml(item.product_id)}">${escapeHtml(item.name)}</a>
        <span class="muted">Size ${escapeHtml(item.size)} · ${formatPrice(item.price)} each</span>
        <button class="link-danger" ${keys} data-qty="0">Remove</button>
      </div>
      <div class="stepper">
        <button ${keys} data-qty="${item.quantity - 1}" aria-label="One less">−</button>
        <span>${item.quantity}</span>
        <button ${keys} data-qty="${item.quantity + 1}" aria-label="One more" ${item.quantity >= 10 ? 'disabled' : ''}>+</button>
      </div>
      <strong class="line-total">${formatPrice(item.line_total)}</strong>
    </li>`;
}
