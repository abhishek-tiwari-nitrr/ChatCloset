// Top bar: logo, category links, orders/admin links and the cart badge. Drawn once at start-up.

export function renderHeader() {
  document.getElementById('header').innerHTML = `
    <div class="container header-inner">
      <a href="#/" class="logo">Cloth<span>Store</span></a>
      <nav class="nav">
        <a href="#/">All</a>
        <a href="#/c/men">Men</a>
        <a href="#/c/women">Women</a>
        <a href="#/c/kids">Kids</a>
      </nav>
      <div class="header-actions">
        <a href="#/orders">Orders</a>
        <a href="#/admin">Admin</a>
        <a href="#/cart" class="cart-link" aria-label="Cart">🛒<span id="cart-count" class="cart-count" hidden>0</span></a>
      </div>
    </div>`;
}

export function updateCartCount(count) {
  const badge = document.getElementById('cart-count');
  badge.textContent = count;
  badge.hidden = count === 0;
}
