/* Portfolio carousel: native horizontal scroll (swipe on phones), arrow
   buttons on wider screens, and Left/Right keys while the strip has focus. */
(function () {
  var track = document.querySelector('[data-track]');
  if (!track) return;
  var prev = document.querySelector('[data-prev]');
  var next = document.querySelector('[data-next]');
  var still = window.matchMedia('(prefers-reduced-motion: reduce)');

  function step() {
    var card = track.querySelector('.work-card');
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return card ? card.getBoundingClientRect().width + gap : track.clientWidth;
  }
  function go(dir) {
    track.scrollBy({ left: dir * step(), behavior: still.matches ? 'auto' : 'smooth' });
  }
  function update() {
    var max = track.scrollWidth - track.clientWidth - 2;
    if (prev) prev.disabled = track.scrollLeft <= 2;
    if (next) next.disabled = track.scrollLeft >= max;
  }

  if (prev) prev.addEventListener('click', function () { go(-1); });
  if (next) next.addEventListener('click', function () { go(1); });
  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
  });
  var raf = 0;
  track.addEventListener('scroll', function () {
    if (!raf) raf = requestAnimationFrame(function () { raf = 0; update(); });
  }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
