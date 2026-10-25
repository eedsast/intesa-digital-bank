/* app.js — page routing between the three views, mobile menu,
   anchor handling that reveals the owning page first, and the
   product modal opened by clicking any catalogue chip. */

(function(){
  var pages = {
    home: document.getElementById('page-home'),
    individuals: document.getElementById('page-individuals'),
    business: document.getElementById('page-business'),
    solution: document.getElementById('page-solution'),
    phases: document.getElementById('page-phases')
  };
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav a[data-nav]'));
  var nav = document.getElementById('nav');
  var menuBtn = document.getElementById('menuBtn');

  function show(name, scroll){
    if(!pages[name]) name = 'home';
    Object.keys(pages).forEach(function(k){ pages[k].hidden = (k !== name); });
    navLinks.forEach(function(a){
      a.classList.toggle('on', a.getAttribute('data-nav') === name && !a.classList.contains('btn'));
    });
    if(scroll !== false) window.scrollTo(0,0);
    nav.classList.remove('open');
    menuBtn.setAttribute('aria-expanded','false');
  }

  document.addEventListener('click', function(e){
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if(!a) return;
    var target = a.getAttribute('data-nav');
    var href = a.getAttribute('href') || '';
    if(target){
      e.preventDefault();
      if(history.replaceState) history.replaceState(null,'', href);
      show(target);
      return;
    }
    // in-page anchor: make sure its page is visible first
    var id = href.slice(1);
    if(!id) return;
    var el = document.getElementById(id);
    if(!el) return;
    var owner = el.closest('main');
    if(owner && owner.hidden){
      e.preventDefault();
      var name = owner.id.replace('page-','');
      show(name, false);
      el.scrollIntoView({behavior:'auto', block:'start'});
      nav.classList.remove('open');
      return;
    }
    nav.classList.remove('open');
    menuBtn.setAttribute('aria-expanded','false');
  });

  menuBtn.addEventListener('click', function(){
    var open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  /* ---------- product modal ---------- */
  var pm = document.getElementById('pm');
  var pmFamily = document.getElementById('pm-family');
  var pmTitle  = document.getElementById('pm-title');
  var pmSections = {
    description:   document.getElementById('pm-desc'),
    prerequisites: document.getElementById('pm-prereq'),
    solution:      document.getElementById('pm-solution'),
    saas:          document.getElementById('pm-saas')
  };
  var lastFocus = null;

  // Which catalogue a chip belongs to: the home panel it sits in, or the page it is on.
  function audienceOf(el){
    if(el.closest('.route--ind')) return 'individuals';
    if(el.closest('.route--biz')) return 'business';
    var main = el.closest('main');
    if(main && main.id === 'page-business') return 'business';
    return 'individuals';
  }

  // The family heading above the chip: <h4> in the home panel, <h3> on a detail card.
  function familyOf(el){
    var box = el.closest('.fam') || el.closest('.card');
    if(!box) return '';
    var h = box.querySelector('h4, h3');
    return h ? h.textContent.trim() : '';
  }

  // A value may be a plain string (description only) or an object with
  // description / prerequisites / solution / saas. Anything absent is "To be defined."
  // Section text may carry light markup (<strong>, <em>, <br>). It comes from
  // products.js, which is part of this site's source, not from user input.
  function fillSection(node, text, fallback){
    if(!node) return;
    node.innerHTML = text || fallback;
    node.classList.toggle('pm-todo', !text);
  }

  function openModal(el){
    var name = el.textContent.trim().replace(/\s+/g,' ');
    var who  = audienceOf(el);
    var data = (window.PRODUCTS || {})[who] || {};
    var entry = data[name];
    var rec = (typeof entry === 'string') ? {description: entry} : (entry || {});
    pm.classList.toggle('pm--biz', who === 'business');
    pmFamily.textContent = familyOf(el);
    pmTitle.textContent  = name;
    fillSection(pmSections.description,   rec.description,
                'No description recorded for this product yet.');
    fillSection(pmSections.prerequisites, rec.prerequisites, 'To be defined.');
    fillSection(pmSections.solution,      rec.solution,      'To be defined.');
    fillSection(pmSections.saas,          rec.saas,          'To be defined.');
    lastFocus = el;
    pm.hidden = false;
    document.body.style.overflow = 'hidden';
    var panel = pm.querySelector('.pm-panel');
    if(panel) panel.focus();
    panel.scrollTop = 0;
  }

  function closeModal(){
    pm.hidden = true;
    document.body.style.overflow = '';
    if(lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
  }

  document.addEventListener('click', function(e){
    if(!e.target.closest) return;
    if(e.target.closest('[data-pm-close]')){ closeModal(); return; }
    var chip = e.target.closest('.fam li, .tag');
    if(chip) openModal(chip);
  });

  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && !pm.hidden){ closeModal(); return; }
    if(e.key !== 'Enter' && e.key !== ' ') return;
    if(!e.target.closest) return;
    var chip = e.target.closest('.fam li, .tag');
    if(chip){ e.preventDefault(); openModal(chip); }
  });

  // make every chip reachable by keyboard
  Array.prototype.forEach.call(document.querySelectorAll('.fam li, .tag'), function(chip){
    chip.setAttribute('tabindex','0');
    chip.setAttribute('role','button');
  });

  var start = (location.hash || '#home').slice(1);
  show(pages[start] ? start : 'home', false);
})();
