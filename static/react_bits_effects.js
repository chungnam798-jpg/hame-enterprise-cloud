// ReactBits Motion & Interaction Engine
document.addEventListener('DOMContentLoaded', () => {
  // Card Spotlight Effect
  const cards = document.querySelectorAll('.stat-card, .metric-card, .card, .dashboard-card, .overview-card');
  cards.forEach(card => {
    card.classList.add('spotlight-card');
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
      card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
    });
  });

  // PWA Service Worker Registration
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(err => {
        console.debug('SW reg skipped:', err);
      });
    });
  }
});
