/**
 * Tryll Engine — trailer clips (<video class="clip">, cut by scripts/site-build/clips.py).
 *
 * Clips ship with a poster and no src, so they never hold up the page:
 *   data-start="load"  (hero) starts once the page has finished loading,
 *   data-start="view"  starts when it scrolls near the screen.
 * Small players get data-src-small. Clips pause off screen and don't play by
 * themselves with reduced motion or Save-Data. A .snd button next to a clip
 * plays it once from the start with sound, then it goes back to a silent loop.
 */
(function () {
    'use strict';

    var clips = Array.prototype.slice.call(document.querySelectorAll('video.clip[data-src]'));
    if (!clips.length) return;
    var still = (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) ||
        !!(navigator.connection && navigator.connection.saveData);
    var loaded = document.readyState === 'complete';

    function play(v) {
        if (!v.getAttribute('src')) {
            var small = v.getAttribute('data-src-small');
            v.src = small && v.getBoundingClientRect().width <= 720 ? small : v.getAttribute('data-src');
        }
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
    }

    function wake(v) {
        if (!still && v.__seen && (loaded || v.getAttribute('data-start') === 'view')) play(v);
    }

    function quiet(v) {
        v.muted = true;
        v.loop = true;
        var b = v.parentNode.querySelector('.snd');
        if (b) {
            b.setAttribute('aria-pressed', 'false');
            b.setAttribute('aria-label', 'Play with sound');
        }
        v.pause();
        wake(v);
    }

    if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                e.target.__seen = e.isIntersecting;
                if (e.isIntersecting) wake(e.target);
                else if (e.target.muted) e.target.pause();
            });
        }, { rootMargin: '200px 0px' });
        clips.forEach(function (v) { io.observe(v); });
    } else {
        clips.forEach(function (v) { v.__seen = true; });
    }

    if (!loaded) {
        window.addEventListener('load', function () {
            loaded = true;
            clips.forEach(wake);
        });
    } else {
        clips.forEach(wake);
    }

    clips.forEach(function (v) {
        v.addEventListener('ended', function () { quiet(v); });
    });

    // A clip cut without its subtitles (data-captions: [from s, to s, line], from
    // config.CLIPS) shows the line being spoken in the .cap next to it, checked on every
    // frame while it plays.
    clips.forEach(function (v) {
        var cap = v.parentNode.querySelector('.cap');
        if (!cap || !v.getAttribute('data-captions')) return;
        var cues = JSON.parse(v.getAttribute('data-captions'));
        var line = cap.firstChild, shown = -1;
        function update() {
            var t = v.currentTime, at = -1;
            for (var i = 0; i < cues.length; i++) if (t >= cues[i][0] && t < cues[i][1]) at = i;
            if (at === shown) return;
            shown = at;
            if (at >= 0) line.textContent = cues[at][2];
            cap.classList.toggle('on', at >= 0);
        }
        function tick() {
            update();
            if (!v.paused) requestAnimationFrame(tick);
        }
        v.addEventListener('play', function () { requestAnimationFrame(tick); });
        v.addEventListener('seeked', update);
    });

    document.addEventListener('click', function (e) {
        var b = e.target.closest && e.target.closest('.snd');
        if (!b) return;
        var v = b.parentNode.querySelector('video.clip');
        if (b.getAttribute('aria-pressed') === 'true') {
            quiet(v);
            return;
        }
        clips.forEach(function (o) { if (o !== v && !o.muted) quiet(o); });   // one voice at a time
        v.loop = false;
        v.muted = false;
        b.setAttribute('aria-pressed', 'true');
        b.setAttribute('aria-label', 'Mute');
        play(v);
        try { v.currentTime = 0; } catch (err) { /* not loaded yet: starts at 0 anyway */ }
    });
})();
