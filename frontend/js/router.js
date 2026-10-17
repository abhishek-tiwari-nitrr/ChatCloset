import { renderHome } from './pages/home.js';
import { renderProduct } from './pages/product.js';
import { renderCart } from './pages/cart.js';
import { renderOrders } from './pages/orders.js';
import { renderAdmin } from './pages/admin.js';
import { escapeHtml } from './ui.js';

const routes = [
    [/^\/$/, renderHome],
    [/^\/c\/(men|women|kids)$/, renderHome],
    [/^\/product\/(\w+)$/, renderProduct],
    [/^\/cart$/, renderCart],
    [/^\/orders$/, renderOrders],
    [/^\/admin$/, renderAdmin],
];

export async function router() {
    const path = location.hash.slice(1) || '/';
    const app = document.getElementById('app');
    document.querySelectorAll('.nav a').forEach((link) => link.classList.toggle('active', link.hash === `#${path}`));
    window.scrollTo(0, 0);
    const route = routes.find(([pattern]) => pattern.test(path));
    if (!route) {
        app.innerHTML = '<p class="empty">Page not found. <a href="#/">Back to the shop</a></p>';
        return;
    }
    const [pattern, render] = route;
    app.innerHTML = '<p class="empty">Loading…</p>';
    try {
        await render(...path.match(pattern).slice(1));
    } catch (error) {
        app.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
    }
}
