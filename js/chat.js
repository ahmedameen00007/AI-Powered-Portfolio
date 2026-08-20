/**
 * js/chat.js
 * OVI Chatbot — Streaming SSE, Markdown Rendering, Mixed AR/EN support.
 * Connects to local Flask RAG server at http://localhost:5050/chat
 */

(function () {
    const API_URL = 'http://localhost:5050/chat';
    const API_KEY_STORAGE = 'ovi_groq_api_key';
    let chatHistory = [];
    let isProcessing = false;

    // ── Load CSS ─────────────────────────────────────────────────────────────
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'css/chat.css';
    document.head.appendChild(link);

    // ── Markdown + RTL/LTR Formatter ─────────────────────────────────────────
    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function inlineFormat(text) {
        // Inline code first to protect its content
        text = text.replace(/`([^`]+)`/g, '<code class="ovi-code">$1</code>');
        // Bold **text**
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Italic *text*
        text = text.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '<em>$1</em>');
        // Links [text](url)
        text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        // Raw URLs (not already linked)
        text = text.replace(/(?<![">])(https?:\/\/[^\s<>"']+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        return text;
    }

    /**
     * Parses raw text into structured HTML with proper dir="auto" per paragraph.
     * Handles: headers, bullet lists, numbered lists, tables, bold, italic, code, URLs.
     * Each block gets dir="auto" so the browser handles RTL/LTR detection automatically.
     */
    function parseMarkdown(rawText) {
        if (!rawText) return '';
        const output = [];
        // Split on one or more blank lines → paragraph blocks
        const blocks = rawText.split(/\n{2,}/);

        for (const block of blocks) {
            const lines = block.split('\n');
            const first = lines[0].trim();

            if (!first) continue;

            // ── Headers ──────────────────────────────────────────────────────
            if (first.startsWith('### ')) {
                output.push(`<h4 class="ovi-h" dir="auto">${inlineFormat(escapeHtml(first.slice(4)))}</h4>`);
                continue;
            }
            if (first.startsWith('## ')) {
                output.push(`<h3 class="ovi-h" dir="auto">${inlineFormat(escapeHtml(first.slice(3)))}</h3>`);
                continue;
            }
            if (first.startsWith('# ')) {
                output.push(`<h2 class="ovi-h" dir="auto">${inlineFormat(escapeHtml(first.slice(2)))}</h2>`);
                continue;
            }

            // ── Horizontal rule ───────────────────────────────────────────────
            if (first === '---' || first === '***' || first === '___') {
                output.push('<hr class="ovi-hr">');
                continue;
            }

            // ── Table ─────────────────────────────────────────────────────────
            if (first.startsWith('|')) {
                let tableHtml = '<div class="ovi-table-wrapper"><table class="ovi-table">';
                let hasHeader = false;
                let tbodyOpen = false;

                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (!line.startsWith('|')) continue;

                    const parts = line.split('|').map(p => p.trim());
                    // Check if it is a separator row (like |---|---| or | :--- |)
                    // Every middle piece is purely dashes, colons, or empty
                    const isSeparator = parts.slice(1, -1).every(p => /^:?-+:?$/.test(p));
                    if (isSeparator && parts.length > 2) {
                        hasHeader = true;
                        continue;
                    }

                    const cells = line.split('|').slice(1, -1).map(c => c.trim());

                    if (!hasHeader && i === 0) {
                        // First line is header
                        tableHtml += '<thead><tr>';
                        cells.forEach(cell => {
                            tableHtml += `<th dir="auto">${inlineFormat(escapeHtml(cell))}</th>`;
                        });
                        tableHtml += '</tr></thead>';
                    } else {
                        if (!tbodyOpen) {
                            tableHtml += '<tbody>';
                            tbodyOpen = true;
                        }
                        tableHtml += '<tr>';
                        cells.forEach(cell => {
                            tableHtml += `<td dir="auto">${inlineFormat(escapeHtml(cell))}</td>`;
                        });
                        tableHtml += '</tr>';
                    }
                }
                if (tbodyOpen) {
                    tableHtml += '</tbody>';
                }
                tableHtml += '</table></div>';
                output.push(tableHtml);
                continue;
            }

            // ── Unordered list ────────────────────────────────────────────────
            if (/^[-*+]\s/.test(first)) {
                const items = lines
                    .map(l => l.trim())
                    .filter(l => /^[-*+]\s/.test(l))
                    .map(l => `<li dir="auto">${inlineFormat(escapeHtml(l.replace(/^[-*+]\s+/, '')))}</li>`);
                output.push(`<ul class="ovi-ul">${items.join('')}</ul>`);
                continue;
            }

            // ── Ordered list ──────────────────────────────────────────────────
            if (/^\d+\.\s/.test(first)) {
                const items = lines
                    .map(l => l.trim())
                    .filter(l => /^\d+\.\s/.test(l))
                    .map(l => `<li dir="auto">${inlineFormat(escapeHtml(l.replace(/^\d+\.\s+/, '')))}</li>`);
                output.push(`<ol class="ovi-ol">${items.join('')}</ol>`);
                continue;
            }

            // ── Regular paragraph ─────────────────────────────────────────────
            // Each line within gets its own dir="auto" <span> joined by <br>,
            // so Arabic and English lines each render in the correct direction.
            const lineSpans = lines
                .map(l => l.trim())
                .filter(l => l.length > 0)
                .map(l => `<span dir="auto" style="display:block">${inlineFormat(escapeHtml(l))}</span>`);
            output.push(`<div class="ovi-para" dir="auto">${lineSpans.join('')}</div>`);
        }

        return output.join('');
    }

    // ── DOM: inject chatbot HTML ──────────────────────────────────────────────
    function ensureChatbotDOM() {
        if (document.getElementById('chatbot')) return;
        const container = document.createElement('div');
        container.innerHTML = `
        <!-- API Key Modal -->
        <div class="ovi-key-modal" id="ovi-key-modal" role="dialog" aria-modal="true">
            <div class="ovi-key-backdrop" id="ovi-key-backdrop"></div>
            <div class="ovi-key-card">
                <button class="ovi-key-close" id="ovi-key-close" aria-label="Close API Key window" type="button">
                    <svg viewBox="0 0 24 24" width="14" height="14" xmlns="http://www.w3.org/2000/svg">
                        <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                        <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                    </svg>
                </button>
                <button class="ovi-key-trash" id="ovi-key-trash" aria-label="Remove API Key" type="button" title="Remove API Key">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
                <div class="ovi-key-logo">
                    <img src="images/Logo.png" alt="Ovi" width="52" height="52">
                </div>
                <h2 class="ovi-key-title" id="ovi-key-title" data-i18n="chat_key_title">Connect to Ovi</h2>
                <p class="ovi-key-desc" id="ovi-key-desc" data-i18n="chat_key_desc">Enter your Groq API key to start chatting with Ahmed's AI assistant.</p>
                <div class="ovi-key-input-wrap">
                    <input type="password" id="ovi-key-input" class="ovi-key-input"
                        placeholder="gsk_••••••••••••••••••••••" autocomplete="off" spellcheck="false" data-i18n-placeholder="chat_key_placeholder">
                    <button class="ovi-key-toggle" id="ovi-key-toggle" aria-label="Show/hide key" type="button">
                        <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
                            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
                        </svg>
                    </button>
                </div>
                <div class="ovi-key-error" id="ovi-key-error"></div>
                <button class="ovi-key-submit" id="ovi-key-submit" type="button" data-i18n="chat_key_submit">Start Chatting</button>
                <a class="ovi-key-link" href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" id="ovi-key-link">Get a free API key →</a>
            </div>
        </div>

        <aside class="chatbot-container is-closed" id="chatbot">
            <div class="chat-header">
                <div class="chat-header-info">
                    <div class="chat-avatar">
                        <img src="images/Logo.png" alt="Ovi" class="chat-avatar-img">
                    </div>
                    <div class="chat-title-wrapper">
                        <h3 id="chat-header-title">Ovi — AI Assistant</h3>
                        <span class="chat-status" id="chat-header-status">Online</span>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                    <button class="chat-key-btn" id="chat-key-btn" aria-label="Change API key" title="Change API Key">
                        <svg viewBox="0 0 24 24" width="15" height="15" xmlns="http://www.w3.org/2000/svg">
                            <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="close-chat" id="close-chat" aria-label="Close chat">
                        <svg viewBox="0 0 24 24" width="16" height="16" xmlns="http://www.w3.org/2000/svg">
                            <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                            <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="typing-indicator" id="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
            <div class="chat-input-form">
                <div class="chat-input-wrapper">
                    <input type="text" id="chat-input" class="chat-input"
                        placeholder="Ask anything about Ahmed..." autocomplete="off">
                </div>
                <button id="send-btn" class="chat-submit-btn" aria-label="Send message">
                    <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
                        <line x1="22" y1="2" x2="11" y2="13"
                            stroke="white" stroke-width="2" stroke-linecap="round"/>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"
                            stroke="white" stroke-width="2" stroke-linejoin="round" fill="none"/>
                    </svg>
                </button>
            </div>
        </aside>

        <div id="chat-trigger" class="chat-trigger">
            <span class="trigger-brand" id="chat-trigger-brand">أثر</span>
            <span class="trigger-text" id="chat-trigger-text">Ovi</span>
        </div>`;
        while (container.firstChild) document.body.appendChild(container.firstChild);
    }

    // ── API Key Management ────────────────────────────────────────────────────
    function getApiKey() {
        const stored = localStorage.getItem(API_KEY_STORAGE) || '';
        // 'server' sentinel means the server already has the key in .env
        return stored;
    }

    function saveApiKey(key) {
        localStorage.setItem(API_KEY_STORAGE, key.trim());
    }

    /**
     * On startup, silently ping /health.
     * If the server responds "ready: true", the GROQ_API_KEY is already
     * loaded from .env — store the sentinel 'server' so we never show the modal.
     */
    async function checkServerKey() {
        try {
            const res = await fetch(API_URL.replace('/chat', '/health'), { method: 'GET' });
            if (res.ok) {
                const data = await res.json();
                if (data.ready) {
                    // Server already has the key — no need for the user to enter one
                    localStorage.setItem(API_KEY_STORAGE, 'server');
                } else {
                    // If the server is not ready and the current key is the 'server' sentinel, clear it
                    if (localStorage.getItem(API_KEY_STORAGE) === 'server') {
                        localStorage.removeItem(API_KEY_STORAGE);
                    }
                }
            }
        } catch (_) {
            // Server unreachable — keep whatever is in localStorage
        }
    }

    function showKeyModal() {
        const modal = document.getElementById('ovi-key-modal');
        const input = document.getElementById('ovi-key-input');
        if (!modal) return;
        modal.classList.add('is-visible');

        // Safe translation helper: falls back to default text if key doesn't exist
        function getTranslation(key, defaultVal) {
            if (window.i18n && typeof window.i18n.t === 'function') {
                const val = window.i18n.t(key);
                if (val && val !== key) return val;
            }
            return defaultVal;
        }

        const title  = document.getElementById('ovi-key-title');
        const desc   = document.getElementById('ovi-key-desc');
        const submit = document.getElementById('ovi-key-submit');

        if (title)  title.textContent  = getTranslation('chat_key_title', 'Connect to Ovi');
        if (desc)   desc.textContent   = getTranslation('chat_key_desc', "Enter your Groq API key to start chatting with Ahmed's AI assistant.");
        if (submit) submit.textContent = getTranslation('chat_key_submit', 'Start Chatting');

        // Sync placeholder and link text separately
        if (input) input.placeholder = getTranslation('chat_key_placeholder', 'gsk_••••••••••••••••••••••');
        const keyLink = document.getElementById('ovi-key-link');
        if (keyLink) keyLink.textContent = getTranslation('chat_key_link', 'Get a free API key →');

        // Pre-fill if key already stored (but don't pre-fill the 'server' sentinel string)
        if (input) {
            const key = getApiKey();
            input.value = (key === 'server') ? '' : key;
        }
        setTimeout(() => { if (input) input.focus(); }, 200);
    }

    function hideKeyModal() {
        const modal = document.getElementById('ovi-key-modal');
        if (modal) modal.classList.remove('is-visible');
    }

    function submitApiKey() {
        const input  = document.getElementById('ovi-key-input');
        const errEl  = document.getElementById('ovi-key-error');
        const t = (window.i18n && window.i18n.t) || (k => k);
        const key = (input ? input.value : '').trim();

        if (!key) {
            // If they cleared the field, remove the saved key
            localStorage.removeItem(API_KEY_STORAGE);
            if (errEl) errEl.style.display = 'none';
            hideKeyModal();
            return;
        }

        if (!key.startsWith('gsk_')) {
            if (errEl) {
                const tr = t('chat_key_invalid');
                errEl.textContent = (tr && tr !== 'chat_key_invalid') ? tr : "Invalid key. Groq API keys start with 'gsk_'";
                errEl.style.display = 'block';
            }
            return;
        }
        if (errEl) errEl.style.display = 'none';
        saveApiKey(key);
        hideKeyModal();
    }

    function initKeyModal() {
        const submitBtn = document.getElementById('ovi-key-submit');
        const toggleBtn = document.getElementById('ovi-key-toggle');
        const keyInput  = document.getElementById('ovi-key-input');
        const backdrop  = document.getElementById('ovi-key-backdrop');
        const changeBtn = document.getElementById('chat-key-btn');
        const closeBtn  = document.getElementById('ovi-key-close');
        const trashBtn  = document.getElementById('ovi-key-trash');

        if (submitBtn) submitBtn.addEventListener('click', submitApiKey);
        if (changeBtn) changeBtn.addEventListener('click', showKeyModal);
        if (closeBtn)  closeBtn.addEventListener('click', hideKeyModal);
        if (backdrop)  backdrop.addEventListener('click', hideKeyModal);
        if (trashBtn) {
            trashBtn.addEventListener('click', () => {
                localStorage.removeItem(API_KEY_STORAGE);
                if (keyInput) keyInput.value = '';
                const errEl = document.getElementById('ovi-key-error');
                if (errEl) errEl.style.display = 'none';
                hideKeyModal();
            });
        }
        if (keyInput) {
            keyInput.addEventListener('keydown', e => {
                if (e.key === 'Enter') submitApiKey();
            });
        }
        if (toggleBtn && keyInput) {
            toggleBtn.addEventListener('click', () => {
                keyInput.type = keyInput.type === 'password' ? 'text' : 'password';
            });
        }
    }

    // ── Translation ───────────────────────────────────────────────────────────
    function translateChatUI() {
        const t = (window.i18n && window.i18n.t) || (k => k);
        const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        set('chat-header-title', t('chat_header_title'));
        set('chat-header-status', t('chat_header_status'));
        set('chat-trigger-brand', t('chat_trigger_brand'));
        set('chat-trigger-text', t('chat_trigger_text'));
        const inp = document.getElementById('chat-input');
        if (inp) inp.placeholder = t('chat_placeholder');

        // Translate the API key modal elements too (fallback to safe values if translations aren't loaded yet)
        const trVal = (key, fallback) => {
            const val = t(key);
            return (val && val !== key) ? val : fallback;
        };
        set('ovi-key-title', trVal('chat_key_title', 'Connect to Ovi'));
        set('ovi-key-desc', trVal('chat_key_desc', "Enter your Groq API key to start chatting with Ahmed's AI assistant."));
        set('ovi-key-submit', trVal('chat_key_submit', 'Start Chatting'));
        const keyInp = document.getElementById('ovi-key-input');
        if (keyInp) keyInp.placeholder = trVal('chat_key_placeholder', 'gsk_••••••••••••••••••••••');
        const keyLink = document.getElementById('ovi-key-link');
        if (keyLink) keyLink.textContent = trVal('chat_key_link', 'Get a free API key →');

        // Always update the greeting so it reflects the current language.
        const area = document.getElementById('chat-messages');
        if (!area) return;
        const existingGreeting = area.querySelector('[data-greeting="true"] .message-bubble');
        const newGreetingHTML = parseMarkdown(t('chat_greeting'));
        if (existingGreeting) {
            existingGreeting.innerHTML = newGreetingHTML;
        } else if (area.querySelectorAll('.message').length === 0) {
            appendMessage(t('chat_greeting'), 'ai', false, true /* isGreeting */);
        }
    }

    // ── Toggle Chat Panel ─────────────────────────────────────────────────────
    function toggleChat(forceClose = false) {
        const chatbot = document.getElementById('chatbot');
        if (!chatbot) return;
        if (forceClose) {
            chatbot.classList.add('is-closed');
            document.body.classList.remove('chat-active');
            hideKeyModal();
        } else {
            chatbot.classList.toggle('is-closed');
            const isOpen = !chatbot.classList.contains('is-closed');
            document.body.classList.toggle('chat-active', isOpen);
            if (isOpen) {
                // If opened and no API key is set yet, show the overlay modal on top of open chat
                if (!getApiKey()) {
                    showKeyModal();
                } else {
                    setTimeout(() => { const i = document.getElementById('chat-input'); if (i) i.focus(); }, 120);
                }
            } else {
                hideKeyModal();
            }
        }
    }

    // ── Append a finished message (with formatting) ───────────────────────────
    function appendMessage(text, sender, stream = false, isGreeting = false) {
        const area = document.getElementById('chat-messages');
        const indicator = document.getElementById('typing-indicator');
        if (!area) return null;

        const div = document.createElement('div');
        div.classList.add('message', sender);
        if (isGreeting) div.setAttribute('data-greeting', 'true');

        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble');
        bubble.setAttribute('dir', 'auto');

        if (sender === 'user') {
            bubble.textContent = text;             // plain text — safe
        } else if (!stream) {
            bubble.innerHTML = parseMarkdown(text); // pre-formatted
        }
        // stream=true → bubble starts empty, filled by streamIntoElem()

        const ts = document.createElement('div');
        ts.classList.add('timestamp');
        ts.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        div.appendChild(bubble);
        div.appendChild(ts);
        if (indicator) area.insertBefore(div, indicator);
        else area.appendChild(div);
        area.scrollTop = area.scrollHeight;
        return bubble;
    }

    // ── Stream tokens into a bubble with typewriter animation ─────────────────
    //
    // Architecture:
    //   1. SSE reader runs async — fills `fullText` as fast as the server sends.
    //   2. Typewriter timer runs independently — reveals chars at CHAR_DELAY ms each.
    //   3. When SSE is finished AND all chars are revealed → render final markdown.
    //
    // This decoupling means the display speed is always smooth (18ms/char) regardless
    // of whether the server sends one token at a time or one big chunk.
    async function streamIntoElem(bubble, reader, area) {
        const CHAR_DELAY  = 18;   // ms between each character reveal
        const MAX_BATCH   = 4;    // chars per tick when catching up (queue > 150 chars behind)

        const decoder = new TextDecoder();
        let sseBuffer  = '';
        let fullText   = '';    // grows as SSE tokens arrive
        let displayed  = 0;    // chars currently shown in the bubble
        let sseDone    = false;

        // Promise that resolves when typewriter finishes
        let resolveTyping;
        const typingFinished = new Promise(r => { resolveTyping = r; });

        // ── Typewriter tick ───────────────────────────────────────────────────
        function tick() {
            const pending = fullText.length - displayed;

            if (pending === 0) {
                if (sseDone) {
                    // All chars shown and stream complete → switch to markdown
                    bubble.innerHTML = parseMarkdown(fullText);
                    area.scrollTop   = area.scrollHeight;
                    resolveTyping();
                    return;
                }
                // No new chars yet; wait a bit for more from the SSE reader
                setTimeout(tick, 30);
                return;
            }

            // Adaptive batch: if very far behind, reveal more chars per tick
            const batch = pending > 150 ? Math.min(Math.ceil(pending / 25), MAX_BATCH) : 1;
            displayed = Math.min(displayed + batch, fullText.length);

            // Show raw text slice + blinking cursor while typing
            bubble.innerHTML = escapeHtml(fullText.slice(0, displayed))
                             + '<span class="ovi-cursor">▍</span>';
            area.scrollTop = area.scrollHeight;

            setTimeout(tick, CHAR_DELAY);
        }

        // Kick off the typewriter animation immediately
        tick();

        // ── SSE reader ───────────────────────────────────────────────────────
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            sseBuffer += decoder.decode(value, { stream: true });
            const lines = sseBuffer.split('\n');
            sseBuffer   = lines.pop(); // hold partial line

            for (const line of lines) {
                const clean = line.trim();
                if (!clean.startsWith('data: ')) continue;
                const data = clean.slice(6).trim();
                if (data === '[DONE]') { sseBuffer = ''; break; }

                try {
                    const parsed = JSON.parse(data);
                    if (parsed.token) {
                        fullText += parsed.token;   // typewriter will pick this up
                    } else if (parsed.error) {
                        throw new Error(parsed.error);
                    }
                } catch (e) {
                    if (e.message && !e.message.startsWith('JSON')) throw e;
                }
            }
        }

        // SSE stream closed — let the typewriter drain whatever remains
        sseDone = true;
        await typingFinished;
        return fullText;
    }


    // ── Send Message ──────────────────────────────────────────────────────────
    async function sendMessage() {
        if (isProcessing) return;
        const inputEl  = document.getElementById('chat-input');
        const sendBtn  = document.getElementById('send-btn');
        const indicator = document.getElementById('typing-indicator');
        const area     = document.getElementById('chat-messages');
        const t = (window.i18n && window.i18n.t) || (k => k);

        if (!inputEl) return;
        const text = inputEl.value.trim();
        if (!text) return;

        // If there is no API key at all, open the modal and keep the typed text
        const apiKey = getApiKey();
        if (!apiKey) {
            showKeyModal();
            return;
        }

        isProcessing = true;
        inputEl.value = '';
        inputEl.disabled = true;
        if (sendBtn) sendBtn.disabled = true;

        appendMessage(text, 'user');
        if (indicator) indicator.style.display = 'flex';
        if (area) area.scrollTop = area.scrollHeight;

        let fullResponseText = '';
        let aiBubble = null;

        try {
            const res = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message:  text.substring(0, 1000),
                    history:  chatHistory.slice(-10),
                    api_key:  apiKey === 'server' ? '' : apiKey
                })
            });

            if (indicator) indicator.style.display = 'none';
            
            if (!res.ok) {
                let errText = `HTTP ${res.status}`;
                try {
                    const errData = await res.json();
                    if (errData && errData.error) errText = errData.error;
                } catch (_) {}
                throw new Error(errText);
            }

            // Create empty AI bubble ready for streaming
            aiBubble = appendMessage('', 'ai', true);

            fullResponseText = await streamIntoElem(aiBubble, res.body.getReader(), area);

            chatHistory.push({ role: 'user',      content: text });
            chatHistory.push({ role: 'assistant', content: fullResponseText });

        } catch (err) {
            console.error('[Ovi]', err);
            if (indicator) indicator.style.display = 'none';
            const trErr = t('chat_error');
            const errMsg = err.message || ((trErr && trErr !== 'chat_error') ? trErr : 'Something went wrong. Please check your backend connection and try again!');
            if (aiBubble) aiBubble.innerHTML = parseMarkdown(errMsg);
            else appendMessage(errMsg, 'ai');
        } finally {
            isProcessing = false;
            inputEl.disabled = false;
            if (sendBtn) sendBtn.disabled = false;
            setTimeout(() => inputEl.focus(), 50);
        }
    }

    // ── Listeners ─────────────────────────────────────────────────────────────
    function initListeners() {
        const trigger  = document.getElementById('chat-trigger');
        const closeBtn = document.getElementById('close-chat');
        const inputEl  = document.getElementById('chat-input');
        const sendBtn  = document.getElementById('send-btn');

        if (trigger)  trigger.addEventListener('click', () => toggleChat());
        if (closeBtn) closeBtn.addEventListener('click', () => toggleChat(true));
        if (inputEl)  inputEl.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        });
        if (sendBtn)  sendBtn.addEventListener('click', sendMessage);
        document.addEventListener('langchange', translateChatUI);
    }

    // ── Boot ──────────────────────────────────────────────────────────────────
    async function init() {
        ensureChatbotDOM();
        initListeners();
        initKeyModal();
        translateChatUI();
        await checkServerKey(); // Check if server has key configured in .env
        console.log('[Ovi Chatbot] Ready.');
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
