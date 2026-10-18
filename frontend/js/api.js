import { state } from './state.js';

async function request(path, options = {}) {
    const response = await fetch(`/api${path}`, options);
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
        const error = new Error(errorText(data) || `Request failed (${response.status})`);
        error.status = response.status;
        throw error;
    }
    return data;
}

// FastAPI sends {detail: "text"} for our errors and {detail: [{msg}, ...]} for validation errors.
function errorText(data) {
    if (!data?.detail) return '';
    return Array.isArray(data.detail) ? data.detail.map((item) => item.msg).join(', ') : data.detail;
}

function query(params) {
    const used = Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '');
    return new URLSearchParams(used).toString();
}

const json = (method, body) => ({ method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
const admin = (method, body) => ({ method, body, headers: { 'X-Admin-Key': state.adminKey } });

export const api = {
    listProducts: (params) => request(`/products?${query(params)}`),
    getProduct: (id) => request(`/products/${encodeURIComponent(id)}`),
    getCart: () => request(`/cart/${state.sessionId}`),
    addToCart: (productId, size, quantity = 1) =>
        request(`/cart/${state.sessionId}/items`, json('POST', { product_id: productId, size, quantity })),
    setQuantity: (productId, size, quantity) =>
        request(`/cart/${state.sessionId}/items`, json('PUT', { product_id: productId, size, quantity })),
    checkout: () => request(`/orders/${state.sessionId}/checkout`, { method: 'POST' }),
    listOrders: () => request(`/orders/${state.sessionId}`),
    createProduct: (form) => request('/products', admin('POST', form)),
    updateProduct: (id, form) => request(`/products/${encodeURIComponent(id)}`, admin('PUT', form)),
    deleteProduct: (id) => request(`/products/${encodeURIComponent(id)}`, admin('DELETE')),
    resetDemo: () => request('/products/reset-demo', admin('POST')),
    chat: (message) => request('/chat', json('POST', { message })),
};
