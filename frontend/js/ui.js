// Small UI helpers shared by every page.

// Escape text before placing it inside HTML, so a product name or chat reply can never inject a script (XSS).
export function escapeHtml(value) {
  const entities = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  return String(value ?? '').replace(/[&<>"']/g, (char) => entities[char]);
}

export const formatPrice = (amount) => `₹${Number(amount).toLocaleString('en-IN')}`;

// A short message that pops up in the corner and disappears after 3 seconds.
export function toast(message, type = 'info') {
  const element = document.createElement('div');
  element.className = `toast toast-${type}`;
  element.textContent = message;
  document.getElementById('toasts').append(element);
  setTimeout(() => element.remove(), 3000);
}

// One product tile, reused everywhere products are listed.
export function productCard(product) {
  const id = escapeHtml(product.id);
  return `
    <article class="card">
      <a href="#/product/${id}" class="card-image"><img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}" loading="lazy" /></a>
      <div class="card-body">
        <span class="badge">${escapeHtml(product.category)}</span>
        <a href="#/product/${id}" class="card-title">${escapeHtml(product.name)}</a>
        <div class="card-footer">
          <strong>${formatPrice(product.price)}</strong>
          <button class="btn btn-small" data-add="${id}" data-size="${escapeHtml(product.sizes[0])}">Add</button>
        </div>
      </div>
    </article>`;
}
