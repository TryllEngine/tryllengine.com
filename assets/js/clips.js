/**
 * Tryll Engine — trailer clips (<video class="clip">, cut by scripts/site-build/clips.py).
 *
 * Clips ship with a poster and no src, so they never hold up the page:
 *   data-start="load"  (hero) starts once the page has finished loading,
 *   data-start="view"  starts when it scrolls near the screen.
 * Small players (in device pixels) get data-src-small. Clips pause off screen and don't play by
 * themselves with reduced motion or Save-Data. A .snd button next to a clip
 * plays it once from the start with sound, then it goes back to a silent loop.
 * Clips with the same data-seq (the Smart NPCs pair) take turns instead of looping: each
 * plays once, then the next one in page order starts, and the last hands back to the first.
 */
(function () {
    'use strict';

    var clips = Array.prototype.slice.call(document.querySelectorAll('video.clip[data-src]'));
    if (!clips.length) return;
    var still = (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) ||
        !!(navigator.connection && navigator.connection.saveData);
    var loaded = document.readyState === 'complete';
    var turn = {};   // data-seq → the clip whose turn it is (at first, the group's first clip)
    clips.forEach(function (v) {
        var seq = v.getAttribute('data-seq');
        if (seq && !turn[seq]) turn[seq] = v;
    });

    function source(v) {
        if (v.getAttribute('src')) return;
        // The small file (640 px wide) when the player is at most ~800 device pixels wide
        // (phones); high-density screens get the full one, so text in a clip stays sharp.
        var small = v.getAttribute('data-src-small');
        var px = v.getBoundingClientRect().width * Math.min(window.devicePixelRatio || 1, 2);
        v.src = small && px <= 800 ? small : v.getAttribute('data-src');
    }

    function play(v) {
        source(v);
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
    }

    // The clip after v in its data-seq group, in page order; the last one hands back to the first.
    function next(v) {
        var seq = v.getAttribute('data-seq');
        var group = clips.filter(function (o) { return o.getAttribute('data-seq') === seq; });
        return group[(group.indexOf(v) + 1) % group.length];
    }

    function wake(v) {
        var seq = v.getAttribute('data-seq');
        if (seq && turn[seq] !== v) return;   // not its turn
        if (still || !v.__seen || !(loaded || v.getAttribute('data-start') === 'view')) return;
        play(v);
        var n = seq && next(v);
        if (n && n !== v && !n.getAttribute('src')) {   // loads while v plays, so it starts at once
            n.preload = 'auto';
            source(n);
        }
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
        v.addEventListener('ended', function () {
            var seq = v.getAttribute('data-seq');
            if (!seq) {
                quiet(v);
                return;
            }
            var n = turn[seq] = next(v);
            try { n.currentTime = 0; } catch (err) { /* not loaded yet: starts at 0 anyway */ }
            wake(n);
        });
        // data-loop-end: a muted clip loops back from here instead of playing to the end;
        // with sound it plays through.
        var end = parseFloat(v.getAttribute('data-loop-end'));
        if (end) v.addEventListener('timeupdate', function () { if (v.muted && v.currentTime >= end) v.currentTime = 0; });
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
        v.addEventListener('ended', function () {   // a clip waiting for its turn shows no line
            shown = -1;
            cap.classList.remove('on');
        });
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
