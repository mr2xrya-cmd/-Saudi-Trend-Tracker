/**
 * Abaq motion helpers (≈1KB minified).
 * - Fallback reveal for browsers without CSS scroll-driven animations.
 * - Count-up numbers in the story section.
 * - Gentle 3D tilt on scent-family cards (fine pointers only).
 * Everything is skipped when motion is off or the visitor prefers reduced motion.
 */
const root = document.documentElement;
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const motionOn = () => root.classList.contains('abaq-motion-on') && !reducedMotion();

function observe(elements, onEnter, options = {}) {
  if (!elements.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      onEnter(entry.target);
      io.unobserve(entry.target);
    });
  }, {rootMargin: '0px 0px -10% 0px', threshold: 0.1, ...options});
  elements.forEach(el => io.observe(el));
}

function initRevealFallback() {
  const supportsScrollTimeline = window.CSS?.supports?.('animation-timeline: view()');
  if (supportsScrollTimeline || !('IntersectionObserver' in window)) return;
  root.classList.add('abaq-io');
  observe([...document.querySelectorAll('[data-abaq-reveal]')], el => el.classList.add('is-in'));
}

function initCounters() {
  const counters = [...document.querySelectorAll('[data-abaq-count]')];
  const format = new Intl.NumberFormat(document.documentElement.lang || 'ar');
  observe(counters, el => {
    const target = Number(el.dataset.abaqCount) || 0;
    const duration = 1600;
    const start = performance.now();
    const tick = now => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4);
      el.textContent = format.format(Math.round(target * eased));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });
}

function initTilt() {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  document.querySelectorAll('.abaq-tilt-group .abaq-family-card').forEach(card => {
    card.addEventListener('pointermove', event => {
      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      card.style.setProperty('--ry', `${(x * 8).toFixed(2)}deg`);
      card.style.setProperty('--rx', `${(-y * 8).toFixed(2)}deg`);
    });
    card.addEventListener('pointerleave', () => {
      card.style.removeProperty('--rx');
      card.style.removeProperty('--ry');
    });
  });
}

export default function initAbaqMotion() {
  if (!motionOn()) return;
  initRevealFallback();
  initCounters();
  initTilt();
}
