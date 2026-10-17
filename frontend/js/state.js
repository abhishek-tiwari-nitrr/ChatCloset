// Shared browser state: who this visitor is (a random id remembered by the browser).

function loadSessionId() {
  let id = localStorage.getItem('clothstore_session');
  if (!id) {
    id = crypto.randomUUID?.() ?? `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('clothstore_session', id);
  }
  return id;
}

export const state = {
  sessionId: loadSessionId(),
};
