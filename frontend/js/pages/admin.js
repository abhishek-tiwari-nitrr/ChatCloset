// Admin page: unlock with the admin key, then add, edit, delete products or reset the demo catalogue.
import { api } from '../api.js';
import { state } from '../state.js';
import { escapeHtml, formatPrice, toast } from '../ui.js';

const SIZES = ['S', 'M', 'L', 'XL', 'XXL'];
let editing = null; // the product being edited, or null while adding a new one
let page = 1;

export async function renderAdmin() {
  const app = document.getElementById('app');
  if (!state.adminKey) {
    app.innerHTML = `
      <form id="unlock" class="panel form narrow">
        <h1 class="page-title">Admin sign-in</h1>
        <input name="key" type="password" placeholder="Admin key (ADMIN_API_KEY in .env)" required autofocus />
        <button class="btn">Unlock</button>
      </form>`;
    document.getElementById('unlock').addEventListener('submit', (event) => {
      event.preventDefault();
      state.adminKey = new FormData(event.target).get('key');
      renderAdmin();
    });
    return;
  }

  const data = await api.listProducts({ page, limit: 10 });
  if (!data.items.length && page > 1) { // the last item of the last page was deleted
    page -= 1;
    return renderAdmin();
  }
  app.innerHTML = `
    <div class="admin-head">
      <h1 class="page-title">Manage products</h1>
      <div class="row-actions">
        <button id="reset" class="btn btn-outline">Reset demo catalogue</button>
        <button id="lock" class="btn btn-outline">Lock</button>
      </div>
    </div>
    <form id="product-form" class="panel form">
      <h2>${editing ? 'Edit product' : 'Add a product'}</h2>
      <div class="form-grid">
        <input name="name" placeholder="Name" required minlength="2" maxlength="80" value="${escapeHtml(editing?.name)}" />
        <input name="price" type="number" placeholder="Price (₹)" required min="1" value="${editing?.price ?? ''}" />
        <select name="category">
          ${['men', 'women', 'kids'].map((c) => `<option ${editing?.category === c ? 'selected' : ''}>${c}</option>`).join('')}
        </select>
        <input name="colors" placeholder="Colours, comma separated" value="${escapeHtml(editing?.colors.join(', ') ?? 'Black')}" />
      </div>
      <textarea name="description" placeholder="Description" required maxlength="500" rows="3">${escapeHtml(editing?.description)}</textarea>
      <div class="chips">
        ${SIZES.map((s) => `<label class="check"><input type="checkbox" name="size" value="${s}" ${!editing || editing.sizes.includes(s) ? 'checked' : ''} /> ${s}</label>`).join('')}
      </div>
      <label class="muted">Image (JPEG, PNG or WebP, max 5 MB${editing ? ', leave empty to keep the current one' : ''})
        <input name="image" type="file" accept="image/jpeg,image/png,image/webp" />
      </label>
      <div class="row-actions">
        <button class="btn" type="submit">${editing ? 'Save changes' : 'Add product'}</button>
        ${editing ? '<button class="btn btn-outline" type="button" id="cancel">Cancel</button>' : ''}
      </div>
    </form>
    <h2 class="section-title">Catalogue (${data.total})</h2>
    <div class="panel table-wrap">
      <table class="table">
        <thead><tr><th></th><th>Name</th><th>Category</th><th>Price</th><th></th></tr></thead>
        <tbody>
          ${data.items.map((p) => `
            <tr>
              <td><img src="${escapeHtml(p.image)}" alt="" class="thumb" /></td>
              <td>${escapeHtml(p.name)}</td>
              <td>${escapeHtml(p.category)}</td>
              <td>${formatPrice(p.price)}</td>
              <td><div class="row-actions">
                <button class="btn btn-small btn-outline" data-edit="${escapeHtml(p.id)}">Edit</button>
                <button class="btn btn-small btn-danger" data-delete="${escapeHtml(p.id)}">Delete</button>
              </div></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div class="pager">
      <button class="btn btn-small btn-outline" data-page="${page - 1}" ${page <= 1 ? 'disabled' : ''}>← Prev</button>
      <span class="muted">Page ${page} of ${data.pages || 1}</span>
      <button class="btn btn-small btn-outline" data-page="${page + 1}" ${page >= data.pages ? 'disabled' : ''}>Next →</button>
    </div>`;

  const form = document.getElementById('product-form');
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const body = new FormData(form);
    body.set('sizes', body.getAll('size').join(','));
    body.delete('size');
    if (!body.get('image').size) body.delete('image'); // no file chosen: keep the current image
    const action = editing ? () => api.updateProduct(editing.id, body) : () => api.createProduct(body);
    run(action, editing ? 'Product updated' : 'Product added', () => { editing = null; });
  });

  document.getElementById('cancel')?.addEventListener('click', () => {
    editing = null;
    renderAdmin();
  });
  document.getElementById('lock').addEventListener('click', () => {
    state.adminKey = '';
    renderAdmin();
  });
  document.getElementById('reset').addEventListener('click', () => {
    if (confirm('Replace the whole catalogue with fresh demo products?')) run(api.resetDemo, 'Demo catalogue restored', () => { page = 1; });
  });
  app.querySelectorAll('[data-edit]').forEach((button) => {
    button.addEventListener('click', () => {
      editing = data.items.find((p) => p.id === button.dataset.edit);
      renderAdmin();
      window.scrollTo(0, 0);
    });
  });
  app.querySelectorAll('[data-delete]').forEach((button) => {
    button.addEventListener('click', () => {
      if (confirm('Delete this product?')) run(() => api.deleteProduct(button.dataset.delete), 'Product deleted');
    });
  });
  app.querySelectorAll('[data-page]').forEach((button) => {
    button.addEventListener('click', () => {
      page = Number(button.dataset.page);
      renderAdmin();
    });
  });
}

// Run an admin action and show the result. On error the form keeps what was typed,
// except for 401 (wrong key): then the key is forgotten and the sign-in form comes back.
async function run(action, successMessage, onSuccess = () => { }) {
  try {
    await action();
    onSuccess();
    toast(successMessage, 'success');
    renderAdmin();
  } catch (error) {
    toast(error.message, 'error');
    if (error.status === 401) {
      state.adminKey = '';
      renderAdmin();
    }
  }
}
