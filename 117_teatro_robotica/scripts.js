// Intersection Observer — reveal animations
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(function(el) { observer.observe(el); });

    // Scroll progress bar
    var progressBar = document.getElementById('scroll-progress');
    window.addEventListener('scroll', function() {
      var progress = Math.min(window.scrollY / (document.documentElement.scrollHeight - window.innerHeight), 1);
      progressBar.style.transform = 'scaleX(' + progress + ')';
    }, { passive: true });

    // Header scroll effect
    var header = document.getElementById('site-header');
    window.addEventListener('scroll', function() {
      header.classList.toggle('scrolled', window.scrollY > 80);
    }, { passive: true });

    // Mobile menu
    var menuOpen = document.getElementById('menu-open');
    var menuClose = document.getElementById('menu-close');
    var mobileMenu = document.getElementById('mobile-menu');
    menuOpen.addEventListener('click', function() { mobileMenu.classList.add('open'); });
    menuClose.addEventListener('click', function() { mobileMenu.classList.remove('open'); });
    mobileMenu.querySelectorAll('.mobile-link').forEach(function(link) {
      link.addEventListener('click', function() { mobileMenu.classList.remove('open'); });
    });

    // Counter animation
    var counterObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var target = parseInt(el.dataset.target);
          var duration = target > 100 ? 2000 : 1200;
          var start = performance.now();
          var animate = function(now) {
            var elapsed = now - start;
            var progress = Math.min(elapsed / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased).toLocaleString('pt-BR');
            if (progress < 1) requestAnimationFrame(animate);
          };
          requestAnimationFrame(animate);
          counterObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('.counter').forEach(function(el) { counterObserver.observe(el); });

    // PARTICLE LOGO EFFECT
    (function() {
      var canvas = document.getElementById('particle-canvas');
      if (!canvas) return;
      var ctx = canvas.getContext('2d');
      var wrap = canvas.parentElement;
      var GAP = 4;
      var SCATTER = 500;
      var CYCLE = 8000;
      var particles = [];
      var W, H, dpr, mouse = {x:-9999,y:-9999}, raf;

      function setup() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        var r = wrap.getBoundingClientRect();
        W = r.width; H = r.height;
        canvas.width = W * dpr; canvas.height = H * dpr;
        ctx.setTransform(dpr,0,0,dpr,0,0);
      }

      function load() {
        var img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = function() {
          var oc = document.createElement('canvas');
          var ox = oc.getContext('2d');
          var sc = Math.min(W/img.width, H/img.height) * 0.85;
          var iw = img.width*sc, ih = img.height*sc;
          oc.width=iw; oc.height=ih;
          ox.drawImage(img,0,0,iw,ih);
          var d = ox.getImageData(0,0,iw,ih).data;
          var offX=(W-iw)/2, offY=(H-ih)/2;
          particles = [];
          for (var y=0; y<ih; y+=GAP) {
            for (var x=0; x<iw; x+=GAP) {
              var i=(y*iw+x)*4;
              if (d[i+3]<128) continue;
              var ang=Math.random()*Math.PI*2;
              var dist=Math.random()*SCATTER;
              particles.push({
                tx:x+offX, ty:y+offY,
                sx:W/2+Math.cos(ang)*dist, sy:H/2+Math.sin(ang)*dist,
                x:W/2+Math.cos(ang)*dist, y:H/2+Math.sin(ang)*dist,
                r:d[i], g:d[i+1], b:d[i+2], a:d[i+3]/255,
                delay:Math.random()*0.3,
                size: 2.5 + Math.random()*1.5
              });
            }
          }
          if (!raf) tick();
        };
        img.src = 'assets/logos/117_teatro_robotica.png';
      }

      function phase(t) {
        if (t<0.25) return {s:'forming', p:t/0.25};
        if (t<0.55) return {s:'formed', p:1};
        if (t<0.80) return {s:'dissolving', p:(t-0.55)/0.25};
        return {s:'dissolved', p:1};
      }

      function tick() {
        raf = requestAnimationFrame(tick);
        ctx.clearRect(0,0,W,H);
        var ct = (performance.now()%CYCLE)/CYCLE;
        var ph = phase(ct);
        for (var i=0; i<particles.length; i++) {
          var p = particles[i];
          var tx, ty, al;
          if (ph.s==='forming') {
            var pr = Math.max(0, Math.min(1, (ph.p - p.delay) / (1 - p.delay)));
            var e = 1 - Math.pow(1 - pr, 3);
            tx = p.sx + (p.tx - p.sx) * e;
            ty = p.sy + (p.ty - p.sy) * e;
            al = 0.3 + e * 0.7;
          } else if (ph.s==='formed') {
            tx = p.tx;
            ty = p.ty;
            al = 1;
          } else if (ph.s==='dissolving') {
            var pr2 = Math.max(0, Math.min(1, (ph.p - p.delay) / (1 - p.delay)));
            var e2 = pr2 * pr2;
            tx = p.tx + (p.sx - p.tx) * e2;
            ty = p.ty + (p.sy - p.ty) * e2;
            al = 1 - e2 * 0.7;
          } else {
            tx = p.sx;
            ty = p.sy;
            al = 0.3;
          }
          p.x += (tx - p.x) * 0.12;
          p.y += (ty - p.y) * 0.12;
          if (ph.s==='formed' || ph.s==='forming') {
            var dx = p.x - mouse.x;
            var dy = p.y - mouse.y;
            var dd = Math.sqrt(dx * dx + dy * dy);
            if (dd < 60) {
              var f = (60 - dd) / 60 * 8;
              p.x += (dx / dd) * f;
              p.y += (dy / dd) * f;
            }
          }
          ctx.globalAlpha = al * p.a;
          ctx.fillStyle = 'rgb(' + p.r + ',' + p.g + ',' + p.b + ')';
          ctx.fillRect(p.x, p.y, p.size, p.size);
        }
        ctx.globalAlpha = 1;
      }

      wrap.addEventListener('mousemove', function(e) {
        var r = canvas.getBoundingClientRect();
        mouse.x = e.clientX - r.left;
        mouse.y = e.clientY - r.top;
      });
      wrap.addEventListener('mouseleave', function() {
        mouse.x = -9999;
        mouse.y = -9999;
      });
      setup();
      load();
      window.addEventListener('resize', function() { setup(); load(); });
    })();
