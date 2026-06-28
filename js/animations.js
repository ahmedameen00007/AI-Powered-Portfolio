/**
 * animations.js
 * Premium scroll-triggered animations using IntersectionObserver API
 * Supports: stagger, directional reveals, scale-ins
 */

/**
 * Initialize scroll-triggered animations with IntersectionObserver
 */
function initAnimations() {
  if (!('IntersectionObserver' in window)) {
    // Fallback: show everything immediately
    document.querySelectorAll('.scroll-reveal').forEach(el => el.classList.add('active'));
    return;
  }

  const observerOptions = {
    root: null,
    rootMargin: '-6% 0px -6% 0px',
    threshold: 0.08,
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        // Once revealed, stop observing for performance
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all scroll-reveal elements
  document.querySelectorAll('.scroll-reveal').forEach(el => {
    observer.observe(el);
  });

  // Also stagger hero badge animations on load
  document.querySelectorAll('.floating-badge').forEach((badge, i) => {
    badge.style.animationDelay = `${i * 1.2}s`;
    badge.style.opacity = '1';
  });
}
