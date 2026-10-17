// Product detail page: big image, description, size picker, "Add to cart" and "Buy now".
import { api } from '../api.js';
import { updateCartCount } from '../components/header.js';
import { escapeHtml, formatPrice, toast } from '../ui.js';

export async function renderProduct(id) {
  const product = await api.getProduct(id);
  const app = document.getElementById('app');
  app.innerHTML = `
    <a href="#/" class="back">← Continue shopping</a>
    <section class="detail">
      <img class="detail-image" src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}" />
      <div class="detail-info">
        <span class="badge">${escapeHtml(product.category)}</span>
        <h1>${escapeHtml(product.name)}</h1>
        <p class="detail-price">${formatPrice(product.price)}</p>
        <p class="muted">${escapeHtml(product.description)}</p>
        <p class="label">Colour: <strong>${escapeHtml(product.colors.join(', '))}</strong></p>
        <p class="label">Size</p>
        <div class="chips">
          ${product.sizes.map((size, i) => `<button class="chip ${i === 0 ? 'active' : ''}" data-pick="${escapeHtml(size)}">${escapeHtml(size)}</button>`).join('')}
        </div>
        <div class="detail-actions">
          <button class="btn" id="add" data-add="${escapeHtml(product.id)}" data-size="${escapeHtml(product.sizes[0])}">Add to cart</button>
          <button class="btn btn-outline" id="buy">Buy now</button>
        </div>
      </div>
    </section>`;

  const addButton = document.getElementById('add');
  app.querySelectorAll('[data-pick]').forEach((chip) => {
    chip.addEventListener('click', () => {
      app.querySelectorAll('[data-pick]').forEach((other) => other.classList.toggle('active', other === chip));
      addButton.dataset.size = chip.dataset.pick; // the global "Add" handler reads this size
    });
  });

  document.getElementById('buy').addEventListener('click', async () => {
    try {
      const cart = await api.addToCart(product.id, addButton.dataset.size);
      updateCartCount(cart.count);
      location.hash = '#/cart';
    } catch (error) {
      toast(error.message, 'error');
    }
  });
}
