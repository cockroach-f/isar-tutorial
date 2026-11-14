/* ISAR 教程自定义视频播放器（无依赖，与 stylesheets/video-player.css 配套）。
 *
 * v2：B 站 / YouTube 式悬浮控制条——控制条以半透明遮罩浮在画面底部，
 * 鼠标移开立刻消失；鼠标静止时也自动隐藏，暂停时藏得更快（0.8 秒），
 * 暂停下来思考时字幕全程可见。遮罩刻意调淡（底部最深处 alpha 0.55），
 * 只求按钮在白色背景的 V 系列视频上仍能看清。控制条只留播放/暂停、
 * 进度、时间、倍速、全屏；快退快进与逐帧只保留键盘（J/L、,/。），
 * 不占控制条位置。
 *
 * 渐进增强：各章 <video controls> 标签不改；本脚本接管后才移除原生
 * controls，脚本失效时原生控制条仍在。视频均无音轨，故无音量控制。
 */
(function () {
  'use strict';

  var SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];
  var STEP = 1 / 30; // 键盘逐帧步长（秒），按 30fps 计
  var SEEK = 5; // 键盘快退 / 快进秒数
  var HIDE_DELAY_PLAYING = 2000; // 播放时鼠标静止多久后隐藏控制条（毫秒）
  var HIDE_DELAY_PAUSED = 800; // 暂停时鼠标静止多久后隐藏：停下 0.8 秒就藏起，不挡字幕
  var SPEED_KEY = 'isar-vp-speed';

  var ICONS = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>',
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

    /* ---------- 悬浮控制条：进度条全宽在上，按钮行在下 ---------- */
    var bar = el('div', 'vp-bar');
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

    var row = el('div', 'vp-controls-row');
    var btnPlay = makeButton('播放', ICONS.play, 'vp-btn-play');
    var time = el('span', 'vp-time');
    time.textContent = '0:00 / 0:00';
    var spacer = el('span', 'vp-spacer');
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
    [btnPlay, time, spacer, speed, btnFull].forEach(function (n) {
      row.appendChild(n);
    });
    bar.appendChild(progress);
    bar.appendChild(row);
    stage.appendChild(bar);
    wrap.appendChild(stage);

    /* ---------- 控制条显隐：移开鼠标立刻消失，静止也自动消失 ---------- */
    var hideTimer = null;
    var hasFocus = false;
    var scrubbing = false;

    function hideNow() {
      if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
      }
      wrap.classList.remove('show-controls');
    }

    function showControls() {
      wrap.classList.add('show-controls');
      if (hideTimer) clearTimeout(hideTimer);
      // 焦点在播放器内或正在拖进度时不自动隐藏；
      // 暂停时鼠标一停就藏（短延迟），播放时留正常延迟
      if (!hasFocus && !scrubbing) {
        var delay = (video.paused || video.ended) ? HIDE_DELAY_PAUSED : HIDE_DELAY_PLAYING;
        hideTimer = setTimeout(hideNow, delay);
      }
    }

    // 鼠标位置去重：控制条藏起后，指针下的元素会从控制条变成画面，
    // 浏览器会补发一次坐标完全相同的 mousemove（悬停重算）；若不去重，
    // 指针停在暂停按钮上时控制条刚藏起来又会被唤回，闪一下才再藏起。
    // 只有坐标真正变化的移动才唤回控制条、重算计时。
    var lastMouseX = null;
    var lastMouseY = null;
    wrap.addEventListener('mouseenter', function (e) {
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      showControls();
    });
    wrap.addEventListener('mousemove', function (e) {
      if (e.clientX === lastMouseX && e.clientY === lastMouseY) return;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      showControls();
    });
    wrap.addEventListener('mouseleave', hideNow); // 移开鼠标：立刻消失
    wrap.addEventListener('touchstart', showControls, { passive: true });
    // 只有焦点落在需要持续操作的控件（进度条、倍速下拉框）上时才钉住控制条；
    // 焦点在容器或播放/全屏按钮上时不钉住——否则点一下画面获得焦点后，
    // 控制条就再也不自动藏了，暂停时仍会挡住字幕。
    function pinsBar(t) {
      return t === progress || t === speed;
    }
    wrap.addEventListener('focusin', function (e) {
      hasFocus = pinsBar(e.target);
      showControls();
    });
    wrap.addEventListener('focusout', function (e) {
      hasFocus = pinsBar(e.relatedTarget);
      if (hasFocus) {
        if (hideTimer) {
          clearTimeout(hideTimer);
          hideTimer = null;
        }
        wrap.classList.add('show-controls');
      } else {
        showControls();
      }
    });

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
        var req = wrap.requestFullscreen();
        if (req && req.catch) req.catch(function () {});
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
      showControls(); // 按播放状态重算隐藏延迟
    });
    video.addEventListener('pause', function () {
      syncPlayBtn();
      showFlash(ICONS.play);
      showControls(); // 暂停后用短延迟：鼠标一停就藏起
    });
    video.addEventListener('ended', function () {
      syncPlayBtn();
      showControls();
    });
    video.addEventListener('timeupdate', syncTime);
    video.addEventListener('loadedmetadata', function () {
      syncTime();
      syncBuffered();
    });
    video.addEventListener('durationchange', syncTime);
    video.addEventListener('progress', syncBuffered);

    // 单击画面切换播放/暂停，双击全屏（单击延迟 260ms 以区分双击）。
    // 控制条现在浮在画面内，点控制条时不触发画面切换。
    var clickTimer = null;
    stage.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('.vp-bar')) return;
      focusWrap();
      if (clickTimer) return;
      clickTimer = setTimeout(function () {
        clickTimer = null;
        toggle();
      }, 260);
    });
    stage.addEventListener('dblclick', function (e) {
      if (e.target.closest && e.target.closest('.vp-bar')) return;
      e.preventDefault();
      if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
      }
      toggleFull();
    });

    btnPlay.addEventListener('click', toggle);
    btnFull.addEventListener('click', toggleFull);
    speed.addEventListener('change', function () {
      video.playbackRate = parseFloat(speed.value);
      saveSpeed(video.playbackRate);
      showControls();
    });

    // 进度拖拽
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
      if (hideTimer) clearTimeout(hideTimer);
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
      showControls();
    });
    progress.addEventListener('pointercancel', function () {
      scrubbing = false;
      showControls();
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
    // 快退快进（J/L）与逐帧（,/。）只保留键盘，不占控制条位置。
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
    showControls(); // 先露一下控制条，静止后自动藏起（暂停 0.8 秒、播放 2 秒）
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
