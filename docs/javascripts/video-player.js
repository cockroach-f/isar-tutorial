/* ISAR 教程自定义视频播放器（无依赖，与 stylesheets/video-player.css 配套）。
 *
 * 解决的问题：浏览器原生 controls 暂停时常驻在画面底部，正好盖住烧录在
 * 画面最底部的字幕；且原生控制条没有倍速、逐帧，不适合"暂停下来想一想"
 * 的学习节奏。本播放器把控制条放在视频画面下方，永不遮挡画面，并提供
 * 倍速（0.5–2×）、±5 秒、逐帧（1/30 秒）、进度拖拽、全屏与键盘控制。
 *
 * 渐进增强：各章 <video controls> 标签不改；本脚本接管后才移除原生
 * controls，脚本失效时原生控制条仍在。视频均无音轨，故无音量控制。
 */
(function () {
  'use strict';

  var SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];
  var STEP = 1 / 30; // 逐帧步长（秒），按 30fps 计
  var SEEK = 5; // 快退 / 快进秒数
  var SPEED_KEY = 'isar-vp-speed';

  var ICONS = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>',
    prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h2v14H6zM20 5v14L9 12z"/></svg>',
    next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 5h2v14h-2zM4 5v14l11-7z"/></svg>',
    full: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>'
  };

  function el(tag, cls) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    return n;
  }

  function pad(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function fmt(t) {
    if (!isFinite(t) || t < 0) t = 0;
    t = Math.floor(t);
    var h = Math.floor(t / 3600);
    var m = Math.floor((t % 3600) / 60);
    var s = t % 60;
    return h ? h + ':' + pad(m) + ':' + pad(s) : m + ':' + pad(s);
  }

  function savedSpeed() {
    try {
      var v = parseFloat(localStorage.getItem(SPEED_KEY));
      return SPEEDS.indexOf(v) >= 0 ? v : 1;
    } catch (e) {
      return 1;
    }
  }

  function saveSpeed(v) {
    try {
      localStorage.setItem(SPEED_KEY, String(v));
    } catch (e) {
      /* 无痕模式等场景下忽略 */
    }
  }

  function makeButton(label, inner, cls) {
    var b = el('button', cls);
    b.type = 'button';
    b.innerHTML = inner;
    b.setAttribute('aria-label', label);
    b.title = label;
    return b;
  }

  function enhance(video) {
    if (!video || video.dataset.vpEnhanced) return;
    video.dataset.vpEnhanced = '1';
    video.removeAttribute('controls');
    video.setAttribute('playsinline', '');
    try {
      video.playsInline = true;
    } catch (e) {
      /* 旧浏览器忽略 */
    }

    var wrap = el('div', 'vp');
    wrap.setAttribute('tabindex', '0');
    wrap.setAttribute('role', 'region');
    wrap.setAttribute('aria-label', '视频播放器');
    var stage = el('div', 'vp-stage');
    var flash = el('div', 'vp-flash');
    flash.setAttribute('aria-hidden', 'true');

    video.parentNode.insertBefore(wrap, video);
    stage.appendChild(video);
    stage.appendChild(flash);
    wrap.appendChild(stage);

    var bar = el('div', 'vp-bar');
    var btnPlay = makeButton('播放', ICONS.play, 'vp-btn-play');
    var btnBack = makeButton('后退 5 秒', '<span class="vp-seek-label">−5s</span>', 'vp-btn-back');
    var btnFwd = makeButton('前进 5 秒', '<span class="vp-seek-label">+5s</span>', 'vp-btn-fwd');
    var btnPrev = makeButton('上一帧', ICONS.prev, 'vp-btn-prev');
    var btnNext = makeButton('下一帧', ICONS.next, 'vp-btn-next');

    var progress = el('div', 'vp-progress');
    progress.setAttribute('role', 'slider');
    progress.setAttribute('tabindex', '0');
    progress.setAttribute('aria-label', '播放进度');
    progress.setAttribute('aria-valuemin', '0');
    progress.setAttribute('aria-valuemax', '100');
    progress.setAttribute('aria-valuenow', '0');
    var buffered = el('div', 'vp-buffered');
    var played = el('div', 'vp-played');
    var thumb = el('div', 'vp-thumb');
    progress.appendChild(buffered);
    progress.appendChild(played);
    progress.appendChild(thumb);

    var time = el('span', 'vp-time');
    time.textContent = '0:00 / 0:00';

    var speed = document.createElement('select');
    speed.className = 'vp-speed';
    speed.setAttribute('aria-label', '播放倍速');
    speed.title = '播放倍速';
    SPEEDS.forEach(function (s) {
      var o = document.createElement('option');
      o.value = String(s);
      o.textContent = (s === 1 ? '1×' : s + '×');
      speed.appendChild(o);
    });

    var btnFull = makeButton('全屏', ICONS.full, 'vp-btn-full');

    [btnPlay, btnBack, btnFwd, btnPrev, btnNext, progress, time, speed, btnFull].forEach(function (n) {
      bar.appendChild(n);
    });
    wrap.appendChild(bar);

    /* ---------- 状态同步 ---------- */
    var flashTimer = null;
    function showFlash(icon) {
      flash.innerHTML = icon;
      flash.classList.add('show');
      if (flashTimer) clearTimeout(flashTimer);
      flashTimer = setTimeout(function () {
        flash.classList.remove('show');
      }, 400);
    }

    function syncPlayBtn() {
      var paused = video.paused || video.ended;
      btnPlay.innerHTML = paused ? ICONS.play : ICONS.pause;
      btnPlay.setAttribute('aria-label', paused ? '播放' : '暂停');
      btnPlay.title = paused ? '播放（空格）' : '暂停（空格）';
    }

    function syncTime() {
      var d = video.duration || 0;
      var c = video.currentTime || 0;
      time.textContent = fmt(c) + ' / ' + fmt(d);
      var p = d > 0 ? Math.min(100, (c / d) * 100) : 0;
      played.style.width = p + '%';
      thumb.style.left = p + '%';
      progress.setAttribute('aria-valuenow', String(Math.round(p)));
      progress.setAttribute('aria-valuetext', Math.round(c) + ' 秒 / ' + Math.round(d) + ' 秒');
    }

    function syncBuffered() {
      try {
        var d = video.duration || 0;
        var b = video.buffered;
        if (d > 0 && b && b.length) {
          buffered.style.width = Math.min(100, (b.end(b.length - 1) / d) * 100) + '%';
        }
      } catch (e) {
        /* 旧实现忽略 */
      }
    }

    /* ---------- 动作 ---------- */
    function toggle() {
      if (video.paused || video.ended) {
        var p = video.play();
        if (p && p.catch) p.catch(function () {});
      } else {
        video.pause();
      }
    }

    function seekBy(delta) {
      var d = video.duration || 0;
      video.currentTime = Math.max(0, Math.min(d, (video.currentTime || 0) + delta));
      syncTime();
    }

    function step(dir) {
      video.pause();
      var d = video.duration || 0;
      video.currentTime = Math.max(0, Math.min(d, (video.currentTime || 0) + dir * STEP));
      syncTime();
    }

    function toggleFull() {
      if (document.fullscreenElement || document.webkitFullscreenElement) {
        var exit = document.exitFullscreen || document.webkitExitFullscreen;
        if (exit) exit.call(document);
      } else if (wrap.requestFullscreen) {
        wrap.requestFullscreen();
      } else if (wrap.webkitRequestFullscreen) {
        wrap.webkitRequestFullscreen();
      } else if (video.webkitEnterFullscreen) {
        video.webkitEnterFullscreen();
      }
    }

    function focusWrap() {
      try {
        wrap.focus({ preventScroll: true });
      } catch (e) {
        wrap.focus();
      }
    }

    /* ---------- 事件 ---------- */
    video.addEventListener('play', function () {
      syncPlayBtn();
      showFlash(ICONS.pause);
    });
    video.addEventListener('pause', function () {
      syncPlayBtn();
      showFlash(ICONS.play);
    });
    video.addEventListener('ended', syncPlayBtn);
    video.addEventListener('timeupdate', syncTime);
    video.addEventListener('loadedmetadata', function () {
      syncTime();
      syncBuffered();
    });
    video.addEventListener('durationchange', syncTime);
    video.addEventListener('progress', syncBuffered);

    // 单击切换播放/暂停，双击全屏（单击延迟 260ms 以区分双击）
    var clickTimer = null;
    stage.addEventListener('click', function () {
      focusWrap();
      if (clickTimer) return;
      clickTimer = setTimeout(function () {
        clickTimer = null;
        toggle();
      }, 260);
    });
    stage.addEventListener('dblclick', function (e) {
      e.preventDefault();
      if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
      }
      toggleFull();
    });

    btnPlay.addEventListener('click', toggle);
    btnBack.addEventListener('click', function () {
      seekBy(-SEEK);
    });
    btnFwd.addEventListener('click', function () {
      seekBy(SEEK);
    });
    btnPrev.addEventListener('click', function () {
      step(-1);
    });
    btnNext.addEventListener('click', function () {
      step(1);
    });
    btnFull.addEventListener('click', toggleFull);
    speed.addEventListener('change', function () {
      video.playbackRate = parseFloat(speed.value);
      saveSpeed(video.playbackRate);
    });

    // 进度拖拽
    var scrubbing = false;
    function fracFromEvent(e) {
      var r = progress.getBoundingClientRect();
      var x = (e.clientX - r.left) / (r.width || 1);
      return Math.max(0, Math.min(1, x));
    }
    function scrubTo(e) {
      var d = video.duration || 0;
      if (!(d > 0)) return;
      video.currentTime = fracFromEvent(e) * d;
      syncTime();
    }
    progress.addEventListener('pointerdown', function (e) {
      scrubbing = true;
      if (progress.setPointerCapture) {
        try {
          progress.setPointerCapture(e.pointerId);
        } catch (err) {
          /* 忽略 */
        }
      }
      scrubTo(e);
    });
    progress.addEventListener('pointermove', function (e) {
      if (scrubbing) scrubTo(e);
    });
    progress.addEventListener('pointerup', function () {
      scrubbing = false;
    });
    progress.addEventListener('pointercancel', function () {
      scrubbing = false;
    });
    progress.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        e.stopPropagation();
        seekBy(-SEEK);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        e.stopPropagation();
        seekBy(SEEK);
      } else if (e.key === 'Home') {
        e.preventDefault();
        e.stopPropagation();
        video.currentTime = 0;
        syncTime();
      } else if (e.key === 'End') {
        e.preventDefault();
        e.stopPropagation();
        video.currentTime = video.duration || 0;
        syncTime();
      }
    });

    // 键盘：只在焦点位于播放器容器/画面/视频本身时响应，
    // 焦点在按钮或倍速下拉框时交给原生行为，避免空格双重触发。
    wrap.addEventListener('keydown', function (e) {
      if (e.target !== wrap && e.target !== video && e.target !== stage) return;
      var k = e.key;
      if (k === ' ' || k === 'k' || k === 'K') {
        e.preventDefault();
        toggle();
      } else if (k === 'j' || k === 'J' || k === 'ArrowLeft') {
        e.preventDefault();
        seekBy(-SEEK);
      } else if (k === 'l' || k === 'L' || k === 'ArrowRight') {
        e.preventDefault();
        seekBy(SEEK);
      } else if (k === ',') {
        e.preventDefault();
        step(-1);
      } else if (k === '.') {
        e.preventDefault();
        step(1);
      } else if (k === 'f' || k === 'F') {
        e.preventDefault();
        toggleFull();
      } else if (k === 'Home') {
        e.preventDefault();
        video.currentTime = 0;
        syncTime();
      } else if (k === 'End') {
        e.preventDefault();
        video.currentTime = video.duration || 0;
        syncTime();
      }
    });

    /* ---------- 初始状态 ---------- */
    var sp = savedSpeed();
    video.playbackRate = sp;
    speed.value = String(sp);
    syncPlayBtn();
    syncTime();
    syncBuffered();
  }

  function init() {
    var videos = document.querySelectorAll('.md-typeset video');
    if (!videos.length) videos = document.querySelectorAll('video[controls]');
    Array.prototype.forEach.call(videos, enhance);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
