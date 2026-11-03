/**
 * Tryll Engine — "What clients are saying" carousel on the homepage.
 *
 * On tablets and phones the carousel shows one or two quote cards at a time, each as
 * tall as its own quote (assets/css/site.css). This fits the carousel's height to the
 * cards in view, so a short quote doesn't sit above the empty space of the longest one;
 * the height eases as you swipe or use the arrows. On desktop every card is in view and
 * the carousel keeps the height of the longest.
 *
 * A change while the carousel is out of sight above the screen (opening /#contact, a
 * resize) happens at once, and what's on screen stays put: browsers with scroll anchoring
 * see to that, others (Safari) get the scroll adjusted here.
 */
(function () {
    'use strict';

    var clip = document.querySelector('.cls .vclip');
    if (!clip || !window.matchMedia) return;
    var cards = clip.querySelectorAll('.card');
    var section = clip.closest('section') || clip;
    var narrow = matchMedia('(max-width: 1100px)');
    var anchoring = !!(window.CSS && CSS.supports && CSS.supports('overflow-anchor', 'auto'));
    var queued = 0, first = true;

    function setHeight(h, instant) {
        if (instant) {
            clip.style.transition = 'none';
            clip.style.height = h;
            void clip.offsetHeight;   // apply it before the transition comes back
            clip.style.transition = '';
        } else {
            clip.style.height = h;
        }
    }

    function fit() {
        queued = 0;
        var box = clip.getBoundingClientRect();
        var above = box.bottom <= 0;
        if (!narrow.matches) {
            if (clip.style.height) setHeight('', true);
            return;
        }
        var h = 0;
        for (var i = 0; i < cards.length; i++) {
            var r = cards[i].getBoundingClientRect();
            // In view: more than half of the card is inside the carousel.
            if (Math.min(r.right, box.right) - Math.max(r.left, box.left) > r.width / 2) h = Math.max(h, r.height);
        }
        h = Math.ceil(h);
        if (!h || Math.abs(h - box.height) < 1) { first = false; return; }
        // What follows the section moves with the carousel's height; when the carousel is above
        // the screen, scroll back by what it actually moved (zero if the browser kept it in place,
        // as it does for a #link while the page loads).
        var below = section.getBoundingClientRect().bottom;
        setHeight(h + 'px', first || above);
        var moved = section.getBoundingClientRect().bottom - below;
        if (above && !anchoring && moved) window.scrollBy(0, moved);
        first = false;
    }

    function later() {
        if (!queued) queued = requestAnimationFrame(fit);
    }

    clip.addEventListener('scroll', later, { passive: true });
    window.addEventListener('resize', later);
    window.addEventListener('load', later);
    if (narrow.addEventListener) narrow.addEventListener('change', later);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(later);   // the text's final wrap
    later();
})();
