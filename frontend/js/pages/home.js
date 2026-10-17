// Home and category pages: hero banner, search + filters, product grid with "Load more".
import { api } from '../api.js';
import { escapeHtml, productCard, toast } from '../ui.js';

const PRICES = [['', 'Any price'], ['0-999', 'Under ₹1,000'], ['1000-2499', '₹1,000 – ₹2,499'], ['2500-', '₹2,500 and above']];
const SORTS = [['newest', 'Newest'], ['price_asc', 'Price: low to high'], ['price_desc', 'Price: high to low']];
const filters = { q: '', price: '', sort: 'newest' }; // remembered while the visitor moves between pages

const HERO = `
  <section class="hero">
    <div class="hero-text">
      <p class="eyebrow">New season collection</p>
      <h1>Clothes you'll love, found in seconds.</h1>
      <p>Curated everyday styles for men, women and kids.</p>
      <div class="hero-actions">
        <a href="#/c/women" class="btn">Shop women</a>
        <a href="#/c/men" class="btn btn-outline">Shop men</a>
      </div>
    </div>
    <div class="hero-art" aria-hidden="true"><span>👗</span><span>🧥</span><span>👕</span></div>
  </section>`;

const options = (list, selected) =>
  list.map(([value, label]) => `<option value="${value}" ${value === selected ? 'selected' : ''}>${label}</option>`).join('');

export async function renderHome(category = '') {
  const app = document.getElementById('app');
  app.innerHTML = `
    ${category ? '' : HERO}
    <section class="toolbar">
      <h2>${category ? escapeHtml(category[0].toUpperCase() + category.slice(1)) : 'All products'}</h2>
      <form id="filters" class="filters">
        <input name="q" type="search" placeholder="Search… e.g. jeans" maxlength="50" value="${escapeHtml(filters.q)}" />
        <select name="price" aria-label="Price">${options(PRICES, filters.price)}</select>
        <select name="sort" aria-label="Sort">${options(SORTS, filters.sort)}</select>
      </form>
    </section>
    <p id="count" class="muted"></p>
    <div id="grid" class="grid"></div>
    <div class="center"><button id="more" class="btn btn-outline" hidden>Load more</button></div>`;

  const form = document.getElementById('filters');
  const grid = document.getElementById('grid');
  const more = document.getElementById('more');
  let page = 1;
  let timer;

  async function load() {
    const [min_price, max_price] = filters.price.split('-');
    const data = await api.listProducts({ category, q: filters.q, min_price, max_price, sort: filters.sort, page, limit: 12 });
    if (page === 1) grid.innerHTML = data.total ? '' : '<p class="empty">No products match your search.</p>';
    grid.insertAdjacentHTML('beforeend', data.items.map(productCard).join(''));
    document.getElementById('count').textContent = `${data.total} products`;
    more.hidden = page >= data.pages;
  }

  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('input', () => {
    clearTimeout(timer); // wait until the visitor stops typing for 300 ms
    timer = setTimeout(() => {
      Object.assign(filters, Object.fromEntries(new FormData(form)));
      page = 1;
      load().catch((error) => toast(error.message, 'error'));
    }, 300);
  });
  more.addEventListener('click', () => {
    page += 1;
    load().catch((error) => toast(error.message, 'error'));
  });
  await load();
}
