/**
 * Tryll Engine — blog listing: topic chips and pagination.
 *
 * Every post card is in the HTML (so crawlers see all links); this only
 * shows one topic / page at a time. Topic and page live in the URL
 * (?topic=News&page=2) so they survive reloads and the back button.
 */
(function () {
    'use strict';

    var PER_PAGE = 12;
    var grid = document.querySelector('.bl .grid');
    if (!grid) return;
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.pc'));
    var chips = Array.prototype.slice.call(document.querySelectorAll('.bl .chips button'));
    var pgn = document.querySelector('.bl .pgn');
    var emp = document.querySelector('.bl .emp');
    var prev = pgn.firstElementChild;
    var next = pgn.lastElementChild;
    var params = new URLSearchParams(location.search);
    var topic = params.get('topic') || 'All';
    var page = Math.max(1, parseInt(params.get('page'), 10) || 1);

    function setUrl() {
        var p = new URLSearchParams();
        if (topic !== 'All') p.set('topic', topic);
        if (page > 1) p.set('page', page);
        var q = p.toString();
        history.replaceState(null, '', location.pathname + (q ? '?' + q : ''));
    }

    function render(scroll) {
        var list = cards.filter(function (c) { return topic === 'All' || c.getAttribute('data-cat') === topic; });
        var pages = Math.max(1, Math.ceil(list.length / PER_PAGE));
        page = Math.min(page, pages);
        cards.forEach(function (c) { c.style.display = 'none'; });
        list.slice((page - 1) * PER_PAGE, page * PER_PAGE).forEach(function (c) { c.style.display = ''; });
        emp.style.display = list.length ? 'none' : 'block';

        while (prev.nextElementSibling !== next) pgn.removeChild(prev.nextElementSibling);
        for (var i = 1; i <= pages; i++) {
            var a = document.createElement('a');
            a.href = '#';
            a.textContent = i;
            a.setAttribute('data-page', i);
            if (i === page) { a.className = 'on'; a.setAttribute('aria-current', 'page'); }
            pgn.insertBefore(a, next);
        }
        prev.className = page === 1 ? 'dis' : '';
        next.className = page === pages ? 'dis' : '';
        pgn.style.display = pages > 1 ? '' : 'none';
        setUrl();
        if (scroll) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    pgn.addEventListener('click', function (e) {
        var a = e.target.closest('a');
        if (!a) return;
        e.preventDefault();
        if (a.className === 'dis') return;
        page = a === prev ? page - 1 : a === next ? page + 1 : +a.getAttribute('data-page');
        render(true);
    });

    chips.forEach(function (b, i) {
        b.addEventListener('click', function () {
            topic = b.textContent.trim();
            page = 1;
            render(false);
        });
        // Restore the chip highlighted by the page logic when ?topic= is set.
        if (b.textContent.trim() === topic && i > 0) setTimeout(function () { b.click(); }, 0);
    });

    render(false);
})();
