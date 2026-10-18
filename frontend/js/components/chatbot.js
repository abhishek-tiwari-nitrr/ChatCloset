// Floating AI shopping assistant. Mounted once, outside the page area, so it survives navigation.
import { api } from '../api.js';
import { escapeHtml, productCard } from '../ui.js';

const SUGGESTIONS = ["Men's jackets under 3000", 'Kids hoodies', 'Dresses above 2000'];

export function mountChatbot() {
    const root = document.getElementById('chatbot');
    root.innerHTML = `
    <button id="chat-toggle" class="chat-toggle" aria-label="Open the shopping assistant">💬</button>
    <section id="chat-panel" class="chat-panel" hidden>
      <header class="chat-head">
        <span>AI shopping assistant</span>
        <button id="chat-close" aria-label="Close">✕</button>
      </header>
      <div id="chat-log" class="chat-log">
        <div class="msg bot">Hi! Tell me what you are looking for.</div>
        <div class="chips">${SUGGESTIONS.map((s) => `<button class="chip" data-ask="${escapeHtml(s)}">${escapeHtml(s)}</button>`).join('')}</div>
      </div>
      <form id="chat-form" class="chat-form">
        <input name="message" placeholder="e.g. women's kurti under 1500" maxlength="500" autocomplete="off" required />
        <button class="btn">Send</button>
      </form>
    </section>`;

    const panel = document.getElementById('chat-panel');
    const log = document.getElementById('chat-log');
    const form = document.getElementById('chat-form');

    const toggle = () => {
        panel.hidden = !panel.hidden;
        if (!panel.hidden) form.message.focus();
    };
    document.getElementById('chat-toggle').addEventListener('click', toggle);
    document.getElementById('chat-close').addEventListener('click', toggle);
    log.addEventListener('click', (event) => {
        const chip = event.target.closest('[data-ask]');
        if (chip) send(chip.dataset.ask);
    });
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        send(form.message.value);
        form.reset();
    });

    async function send(text) {
        if (!text.trim()) return;
        addToLog(`<div class="msg user">${escapeHtml(text)}</div>`);
        const typing = addToLog('<div class="msg bot typing">Thinking…</div>');
        try {
            const answer = await api.chat(text.trim());
            typing.remove();
            addToLog(`<div class="msg bot">${escapeHtml(answer.reply)}</div>`);
            if (answer.products.length) addToLog(`<div class="chat-products">${answer.products.map(productCard).join('')}</div>`);
        } catch (error) {
            typing.remove();
            addToLog(`<div class="msg bot error">${escapeHtml(error.message)}</div>`);
        }
    }

    function addToLog(html) {
        log.insertAdjacentHTML('beforeend', html);
        log.scrollTop = log.scrollHeight;
        return log.lastElementChild;
    }
}
