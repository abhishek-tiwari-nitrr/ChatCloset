import { api } from './api.js';
import { renderHeader, updateCartCount } from './components/header.js';
import { router } from './router.js';
import { toast } from './ui.js';

renderHeader();
window.addEventListener('hashchange', router);
router();
api.getCart().then((cart) => updateCartCount(cart.count)).catch(() => { });


document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-add]');
    if (!button) return;
    button.disabled = true;
    try {
        const cart = await api.addToCart(button.dataset.add, button.dataset.size);
        updateCartCount(cart.count);
        toast('Added to cart', 'success');
    } catch (error) {
        toast(error.message, 'error');
    } finally {
        button.disabled = false;
    }
});
