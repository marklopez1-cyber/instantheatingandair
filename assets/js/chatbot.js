/* =========================================================================
   Instant Heating and Air — on-site chatbot widget
   -------------------------------------------------------------------------
   Self-contained vanilla JS. No dependencies. No external API calls (except
   to /assets/data/iha-knowledge.json, which is hosted by us).

   Behavior:
     - Floating launcher button bottom-right of every page
     - Tap to open a chat panel
     - Greets with quick-reply chips powered by knowledge JSON
     - Pattern-matches user free text against INTENTS in the knowledge file
     - Renders responses (HTML allowed) + action chips (call / link / modal / quick)
     - Falls back to phone + contact form when no intent matches
     - Fires GA4 events for every interaction (already wired site-wide)
     - Remembers panel open/closed state via sessionStorage
   ========================================================================= */

(function () {
  'use strict';

  // ---- Config ------------------------------------------------------------
  // Cache-bust the knowledge URL on each page load so browsers can't serve
  // a stale copy that's missing newer intents. Daily granularity is plenty —
  // we don't redeploy intra-day often enough to need finer.
  var KNOWLEDGE_URL = '/assets/data/iha-knowledge.json?v=' + new Date().toISOString().slice(0, 10);
  var STORAGE_KEY = 'iha_chat_open';
  var MATCH_THRESHOLD = 0.5;

  // ---- State -------------------------------------------------------------
  var knowledge = null;
  var historyMessages = [];

  // ---- Boot --------------------------------------------------------------
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // Don't render the widget on the 404 / thanks / privacy / terms pages —
    // they're either error states or destinations after a form submit.
    var path = window.location.pathname;
    if (/(\/404\.html|\/thanks\.html)$/.test(path)) return;

    fetch(KNOWLEDGE_URL, { credentials: 'omit' })
      .then(function (r) {
        if (!r.ok) throw new Error('knowledge fetch failed: ' + r.status);
        return r.json();
      })
      .then(function (data) {
        knowledge = data;
        renderWidget();
      })
      .catch(function (err) {
        // Silently fail. The widget just won't appear, no harm done.
        if (window.console) console.warn('[chatbot] disabled:', err && err.message);
      });
  }

  // ---- DOM construction --------------------------------------------------
  function renderWidget() {
    var root = document.createElement('div');
    root.className = 'chatbot-root';
    root.innerHTML = [
      '<button type="button" class="chatbot-launcher" aria-label="Open chat with Instant Heating and Air" aria-expanded="false">',
      '  <span class="chatbot-launcher-icon" aria-hidden="true">💬</span>',
      '  <span class="chatbot-launcher-label">Ask us</span>',
      '</button>',
      '<aside class="chatbot-panel" role="dialog" aria-label="Instant Heating and Air assistant" hidden>',
      '  <header class="chatbot-header">',
      '    <div class="chatbot-header-info">',
      '      <div class="chatbot-avatar" aria-hidden="true">IHA</div>',
      '      <div>',
      '        <strong>Instant Heating and Air</strong>',
      '        <span class="chatbot-status"><span class="chatbot-dot"></span> Live · usually replies fast</span>',
      '      </div>',
      '    </div>',
      '    <button type="button" class="chatbot-close" aria-label="Close chat">×</button>',
      '  </header>',
      '  <div class="chatbot-log" role="log" aria-live="polite"></div>',
      '  <form class="chatbot-form" autocomplete="off">',
      '    <input type="text" class="chatbot-input" placeholder="Type a question…" aria-label="Type a question for the assistant" maxlength="500">',
      '    <button type="submit" class="chatbot-send" aria-label="Send message">→</button>',
      '  </form>',
      '  <footer class="chatbot-footer">',
      '    Replies are generated. For urgent matters, call <a href="tel:' + escAttr(knowledge.company.phone_link) + '">' + esc(knowledge.company.phone_display) + '</a>.',
      '  </footer>',
      '</aside>'
    ].join('');
    document.body.appendChild(root);

    var launcher = root.querySelector('.chatbot-launcher');
    var panel = root.querySelector('.chatbot-panel');
    var closeBtn = root.querySelector('.chatbot-close');
    var form = root.querySelector('.chatbot-form');
    var input = root.querySelector('.chatbot-input');
    var log = root.querySelector('.chatbot-log');

    launcher.addEventListener('click', function () { open(panel, launcher, input); });
    closeBtn.addEventListener('click', function () { close(panel, launcher); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = input.value.trim();
      if (!q) return;
      input.value = '';
      handleUserMessage(q, log);
    });

    // Greet on first open
    renderGreeting(log);

    // Restore open state across navigation
    try {
      if (sessionStorage.getItem(STORAGE_KEY) === '1') {
        open(panel, launcher, null);
      }
    } catch (e) { /* ignore */ }

    track('chatbot_ready');
  }

  function open(panel, launcher, input) {
    panel.hidden = false;
    launcher.setAttribute('aria-expanded', 'true');
    launcher.classList.add('is-open');
    try { sessionStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    if (input) {
      setTimeout(function () { input.focus(); }, 200);
    }
    track('chatbot_open');
  }

  function close(panel, launcher) {
    panel.hidden = true;
    launcher.setAttribute('aria-expanded', 'false');
    launcher.classList.remove('is-open');
    try { sessionStorage.setItem(STORAGE_KEY, '0'); } catch (e) {}
    track('chatbot_close');
  }

  // ---- Conversation rendering -------------------------------------------
  function renderGreeting(log) {
    var greeting = knowledge.chatbot && knowledge.chatbot.greeting
      ? knowledge.chatbot.greeting
      : 'Hi! I can help with HVAC questions, scheduling, pricing, and more.';
    appendBotMessage(log, greeting, []);

    var chips = (knowledge.chatbot && knowledge.chatbot.quick_replies) || [];
    if (chips.length) appendQuickReplies(log, chips);
  }

  function appendUserMessage(log, text) {
    var msg = document.createElement('div');
    msg.className = 'chatbot-msg chatbot-msg-user';
    msg.innerHTML = '<div class="chatbot-bubble">' + esc(text) + '</div>';
    log.appendChild(msg);
    historyMessages.push({ role: 'user', text: text });
    scrollLog(log);
  }

  function appendBotMessage(log, html, actions) {
    var msg = document.createElement('div');
    msg.className = 'chatbot-msg chatbot-msg-bot';
    msg.innerHTML =
      '<div class="chatbot-avatar chatbot-avatar-sm" aria-hidden="true">IHA</div>' +
      '<div class="chatbot-bubble">' + html + '</div>';
    log.appendChild(msg);

    if (actions && actions.length) {
      var row = document.createElement('div');
      row.className = 'chatbot-actions';
      actions.forEach(function (a) {
        row.appendChild(buildActionButton(a, log));
      });
      log.appendChild(row);
    }

    historyMessages.push({ role: 'bot', text: stripHtml(html) });
    scrollLog(log);
  }

  function appendQuickReplies(log, replies) {
    var row = document.createElement('div');
    row.className = 'chatbot-quick-replies';
    replies.forEach(function (r) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chatbot-chip';
      btn.textContent = r.label;
      btn.addEventListener('click', function () {
        handleUserMessage(r.query, log);
      });
      row.appendChild(btn);
    });
    log.appendChild(row);
    scrollLog(log);
  }

  function buildActionButton(action, log) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chatbot-action chatbot-action-' + (action.kind || 'link');
    btn.textContent = action.label || 'Learn more';

    btn.addEventListener('click', function () {
      track('chatbot_action_' + (action.kind || 'link'), { target: action.target });
      switch ((action.kind || 'link').toLowerCase()) {
        case 'call':
          // Phone dialer
          window.location.href = 'tel:' + action.target;
          break;
        case 'modal':
          // Trigger an existing modal (e.g. estimate-modal)
          var trigger = document.querySelector('[data-modal-open="' + action.target + '"]');
          if (trigger) {
            trigger.click();
          } else {
            // Fallback: navigate to contact page
            window.location.href = '/contact.html';
          }
          break;
        case 'quick':
          // Treat as if the user typed this
          handleUserMessage(action.target, log);
          break;
        case 'intent':
          // Direct intent dispatch by ID — bypasses pattern matching so the
          // chosen intent fires deterministically, no matter how its response
          // text overlaps with other intents.
          var intentsArr = (knowledge.chatbot && knowledge.chatbot.intents) || [];
          var matched = null;
          for (var i = 0; i < intentsArr.length; i++) {
            if (intentsArr[i].id === action.target) { matched = intentsArr[i]; break; }
          }
          if (matched) {
            appendUserMessage(log, action.label || matched.id);
            track('chatbot_intent_dispatch', { intent: matched.id });
            var typing = appendTypingIndicator(log);
            setTimeout(function () {
              typing.remove();
              appendBotMessage(log, matched.response, matched.actions || []);
            }, 280 + Math.random() * 220);
          } else {
            // Intent ID not found — fall back to natural-language matching
            handleUserMessage(action.label || action.target, log);
          }
          break;
        case 'link':
        default:
          // External link in new tab, internal in same tab
          if (/^https?:\/\//i.test(action.target)) {
            window.open(action.target, '_blank', 'noopener');
          } else {
            window.location.href = action.target;
          }
      }
    });

    return btn;
  }

  // ---- Intent matching ---------------------------------------------------
  function handleUserMessage(text, log) {
    appendUserMessage(log, text);
    track('chatbot_user_message', { text: text.substring(0, 100) });

    var typing = appendTypingIndicator(log);
    // Tiny delay so it feels conversational
    setTimeout(function () {
      typing.remove();
      var match = matchIntent(text);
      track('chatbot_intent_match', { intent: match.id, score: match.score });
      appendBotMessage(log, match.response, match.actions || []);
    }, 280 + Math.random() * 220);
  }

  function matchIntent(text) {
    var lower = (text || '').toLowerCase();
    var intents = (knowledge.chatbot && knowledge.chatbot.intents) || [];
    var threshold = (knowledge.chatbot && knowledge.chatbot.match_threshold) || MATCH_THRESHOLD;

    var bestScore = 0;
    var bestIntent = null;

    intents.forEach(function (intent) {
      (intent.patterns || []).forEach(function (pattern) {
        // pattern is array of required keywords. All must be present (in any order)
        // for the pattern to score. Score = (matched / total in pattern) for now.
        var matched = pattern.filter(function (keyword) {
          return lower.indexOf(keyword.toLowerCase()) !== -1;
        }).length;
        if (matched === pattern.length && pattern.length > 0) {
          // Reward longer-pattern (more specific) matches over short ones.
          var score = pattern.length / Math.max(pattern.length, 1) + (pattern.length * 0.1);
          if (score > bestScore) {
            bestScore = score;
            bestIntent = intent;
          }
        }
      });
    });

    if (bestIntent && bestScore >= threshold) {
      return {
        id: bestIntent.id,
        score: bestScore,
        response: bestIntent.response,
        actions: bestIntent.actions || [],
      };
    }

    // Fallback
    var fb = (knowledge.chatbot && knowledge.chatbot.fallback) || {
      id: 'fallback',
      response: "I can't quite parse that — try calling " + esc(knowledge.company.phone_display) + " or use the contact form.",
      actions: [],
    };
    return {
      id: fb.id,
      score: 0,
      response: fb.response,
      actions: fb.actions || [],
    };
  }

  function appendTypingIndicator(log) {
    var t = document.createElement('div');
    t.className = 'chatbot-msg chatbot-msg-bot chatbot-typing';
    t.innerHTML =
      '<div class="chatbot-avatar chatbot-avatar-sm" aria-hidden="true">IHA</div>' +
      '<div class="chatbot-bubble"><span class="chatbot-dot-anim"></span><span class="chatbot-dot-anim"></span><span class="chatbot-dot-anim"></span></div>';
    log.appendChild(t);
    scrollLog(log);
    return t;
  }

  // ---- Utilities ---------------------------------------------------------
  function scrollLog(log) {
    log.scrollTop = log.scrollHeight;
  }

  function esc(s) {
    return String(s || '').replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  function escAttr(s) { return esc(s); }

  function stripHtml(html) {
    var d = document.createElement('div');
    d.innerHTML = html;
    return d.textContent || '';
  }

  function track(name, params) {
    try {
      if (window.gtag) window.gtag('event', name, params || {});
      if (window.dataLayer) window.dataLayer.push(Object.assign({ event: name }, params || {}));
    } catch (e) { /* ignore */ }
  }
})();
