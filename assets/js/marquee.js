/**
 * Tryll Engine — media logos row on the homepage.
 *
 * The row scrolls with a CSS animation (tryll-logos in assets/css/site.css), which
 * the browser runs smoothly off the main thread. This keeps the design's "on"
 * highlight on the logo passing the middle, timed from that same animation
 * (the design did both from its 25 fps logic tick, which stuttered). Away from
 * the screen the row holds still, so the browser has no frames to draw for it.
 */
(function () {
    'use strict';

    var track = document.querySelector('.mtrack');
    if (!track || !track.getAnimations) return;
    var logos = track.querySelectorAll('.logo');
    var GROUP = 5, SPEED = 0.28;   // logos per set, logos per second (design: LGW, LSPD)
    var last = -1;
    var near = true;

    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
            near = entries[entries.length - 1].isIntersecting;
            track.style.animationPlayState = near ? '' : 'paused';   // '' leaves it to site.css (hover)
        }, { rootMargin: '100px 0px' }).observe(track.parentNode);
    }

    function tick() {
        if (!near) return;
        var a = track.getAnimations()[0];
        var t = a && a.currentTime != null ? a.currentTime / 1000 : 0;
        var on = Math.round(GROUP + (t * SPEED) % GROUP) % GROUP;
        if (on === last) return;
        last = on;
        for (var i = 0; i < logos.length; i++) logos[i].classList.toggle('on', i % GROUP === on);
    }

    tick();
    setInterval(tick, 100);
})();
