const grid = document.getElementById('grid');
const filters = document.getElementById('filters');

function escapeHtml(value) {
    const entities = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
    return String(value ?? '').replace(/[&<>"']/g, (char) => entities[char]);
}

const formatPrice = (amount) => `₹${Number(amount).toLocaleString('en-IN')}`;

function productCard(product) {
    return `
    <article class="card">
      <div class="card-image"><img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}" loading="lazy" /></div>
      <div class="card-body">
        <span class="badge">${escapeHtml(product.category)}</span>
        <h3 class="card-title">${escapeHtml(product.name)}</h3>
        <div class="card-footer"><strong>${formatPrice(product.price)}</strong></div>
      </div>
    </article>`;
}

async function loadProducts() {
    const category = location.hash.slice(1);
    const [minPrice, maxPrice] = filters.price.value.split('-');
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    if (minPrice) params.set('min_price', minPrice);
    if (maxPrice) params.set('max_price', maxPrice);

    document.getElementById('title').textContent = category ? category[0].toUpperCase() + category.slice(1) : 'All products';
    document.querySelectorAll('.nav a').forEach((link) => link.classList.toggle('active', link.dataset.category === category));

    const response = await fetch(`/api/products?${params}`);
    if (!response.ok) {
        grid.innerHTML = '<p class="empty">Could not load products. Is the server running?</p>';
        return;
    }
    const products = await response.json();
    document.getElementById('count').textContent = `${products.length} products`;
    grid.innerHTML = products.length ? products.map(productCard).join('') : '<p class="empty">No products match this filter.</p>';
}

window.addEventListener('hashchange', loadProducts);
filters.addEventListener('change', loadProducts);
loadProducts();
