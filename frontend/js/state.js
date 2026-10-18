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
  get adminKey() {
    return sessionStorage.getItem('clothstore_admin_key') || '';
  },
  set adminKey(value) {
    if (value) sessionStorage.setItem('clothstore_admin_key', value);
    else sessionStorage.removeItem('clothstore_admin_key');
  },
};