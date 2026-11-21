/* Next Digital Level — colour theme preference.
   The theme is a data attribute on <html>, read before first paint by the
   inline script in <head>. The site is English-only: every page is written
   in English, and NDL_LANG tells the other scripts to use their English copy. */
(function () {
  'use strict';
  const doc = document.documentElement;
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  let theme = doc.dataset.theme === 'dark' ? 'dark' : 'light';
  window.NDL_LANG = 'en';

  /* ---------- Theme ---------- */
  function setTheme(next) {
    theme = next;
    if (next === 'dark') doc.dataset.theme = 'dark'; else delete doc.dataset.theme;
    try { localStorage.setItem('ndl-theme', next); } catch (e) { /* ignore */ }
    document.dispatchEvent(new Event('ndl:theme'));
    $$('[data-theme-toggle]').forEach(b => b.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'));
  }
  $$('[data-theme-toggle]').forEach(b => b.addEventListener('click', () => setTheme(theme === 'dark' ? 'light' : 'dark')));
  setTheme(theme);
})();
