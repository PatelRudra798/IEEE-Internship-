// Frontend Logic for Gemini Token Studio
let chatHistory = [];
let activeTab = 'chat';
let activeStreamController = null;

// Session token counters
let sessionPromptTokens = 0;
let sessionCompletionTokens = 0;
let sessionTotalTokens = 0;
const SESSION_LIMIT = 5000; // Visual limit representation

// Initialize UI elements when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupSliders();
    setupTextareaAutoHeight();
    
    // Set initial Live Tokenizer text
    const tokenizerInput = document.getElementById('tokenizer-input-text');
    if (tokenizerInput) {
        tokenizerInput.value = "Gemini models process text using tokens. Try typing here to see how it tokenizes!";
        handleTokenizerInput();
    }
});

// Tab Switching
function switchTab(tabName) {
    activeTab = tabName;
    
    // Toggle navigation buttons
    document.getElementById('nav-chat-tab').classList.toggle('active', tabName === 'chat');
    document.getElementById('nav-tokenizer-tab').classList.toggle('active', tabName === 'tokenizer');
    
    // Toggle views
    document.getElementById('tab-chat').classList.toggle('workspace-tabactive', tabName === 'chat');
    document.getElementById('tab-tokenizer').classList.toggle('workspace-tabactive', tabName === 'tokenizer');
}

// Sync sliders with value labels
function setupSliders() {
    const sliders = [
        { id: 'temperature-slider', valId: 'temperature-value', fix: 2 },
        { id: 'top-p-slider', valId: 'top-p-value', fix: 2 },
        { id: 'top-k-slider', valId: 'top-k-value', fix: 0 }
    ];

    sliders.forEach(slider => {
        const el = document.getElementById(slider.id);
        const valEl = document.getElementById(slider.valId);
        if (el && valEl) {
            el.addEventListener('input', (e) => {
                let val = parseFloat(e.target.value);
                valEl.textContent = slider.fix > 0 ? val.toFixed(slider.fix) : val;
            });
        }
    });

    // Max Output Tokens checkbox toggle
    const enableCheckbox = document.getElementById('enable-max-tokens');
    const maxSlider = document.getElementById('max-tokens-slider');
    const maxValLabel = document.getElementById('max-tokens-value');
    if (enableCheckbox && maxSlider && maxValLabel) {
        enableCheckbox.addEventListener('change', () => {
            const enabled = enableCheckbox.checked;
            maxSlider.disabled = !enabled;
            maxSlider.style.opacity = enabled ? '1' : '0.3';
            maxValLabel.style.opacity = enabled ? '1' : '0.4';
            maxValLabel.textContent = enabled ? maxSlider.value : 'off';
        });
        maxSlider.addEventListener('input', () => {
            if (enableCheckbox.checked) {
                maxValLabel.textContent = maxSlider.value;
            }
        });
    }
}

// Auto-growing chat textarea input
function setupTextareaAutoHeight() {
    const tx = document.getElementById('chat-input');
    if (tx) {
        tx.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight - 4) + 'px';
        });
        
        // Enter submits form, Shift+Enter adds new line
        tx.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                document.getElementById('chat-form').requestSubmit();
            }
        });
    }
}

// Manage Warning Banner
function showCutoffWarning(limit) {
    const banner = document.getElementById('cutoff-warning-banner');
    const msgText = document.getElementById('warning-message-text');
    msgText.textContent = `The response was cut off because it reached the Max Output Tokens limit of ${limit} tokens.`;
    banner.classList.remove('hidden');
}

function dismissWarning() {
    document.getElementById('cutoff-warning-banner').classList.add('hidden');
}

// Update token progress bar
function updateSessionProgress() {
    document.getElementById('session-prompt-tokens').textContent = sessionPromptTokens;
    document.getElementById('session-completion-tokens').textContent = sessionCompletionTokens;
    document.getElementById('session-total-tokens').textContent = sessionTotalTokens;

    const percent = Math.min(100, Math.round((sessionTotalTokens / SESSION_LIMIT) * 100));
    document.getElementById('progress-percent').textContent = percent;
    
    const fill = document.getElementById('progress-fill');
    fill.style.width = `${percent}%`;
    
    // Change color based on fullness
    if (percent > 85) {
        fill.style.background = 'linear-gradient(to right, #f43f5e, #e11d48)'; // Red alert
    } else if (percent > 60) {
        fill.style.background = 'linear-gradient(to right, #eab308, #ca8a04)'; // Orange warning
    } else {
        fill.style.background = 'linear-gradient(to right, var(--primary), var(--secondary))'; // Standard gradient
    }
}

// Clear Session
function clearChatHistory() {
    chatHistory = [];
    sessionPromptTokens = 0;
    sessionCompletionTokens = 0;
    sessionTotalTokens = 0;
    updateSessionProgress();
    dismissWarning();
    
    // Reset Chat message area
    const area = document.getElementById('chat-messages');
    area.innerHTML = `
        <div class="welcome-box" id="welcome-message">
            <div class="welcome-gemini-gradient"></div>
            <h2>Welcome to Gemini Token Studio</h2>
            <p>This interactive chat environment demonstrates <strong>Tokenization</strong> and <strong>Generation Limits</strong>. In LLMs, text is processed in chunks called <em>tokens</em> (roughly 4 characters each).</p>
            <div class="welcome-features">
                <div class="feature-card">
                    <h3>💡 Streaming Tokens</h3>
                    <p>Watch responses generate segment by segment in real-time, just like Gemini.</p>
                </div>
                <div class="feature-card">
                    <h3>🎨 Visual Tokenizer</h3>
                    <p>Toggle <strong>"View Tokens"</strong> on any response to highlight exactly how text is split into subwords.</p>
                </div>
                <div class="feature-card">
                    <h3>⚡ Limit Enforcement</h3>
                    <p>Lower the <em>Max Output Tokens</em> slider and ask a long question to see the response get cut off.</p>
                </div>
            </div>
        </div>
    `;
}

// Handle Chat Submission
async function handleChatSubmit(event) {
    event.preventDefault();
    
    const inputEl = document.getElementById('chat-input');
    const userMsg = inputEl.value.trim();
    if (!userMsg) return;
    
    // Reset input height & value
    inputEl.value = '';
    inputEl.style.height = 'auto';
    dismissWarning();
    
    // Hide welcome message if present
    const welcome = document.getElementById('welcome-message');
    if (welcome) welcome.remove();
    
    const messagesArea = document.getElementById('chat-messages');
    
    // 1. Render User Message
    appendMessageHTML('user', userMsg);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    // Grab configuration values
    const model = document.getElementById('model-select').value;
    const temp = parseFloat(document.getElementById('temperature-slider').value);
    const maxTokensEnabled = document.getElementById('enable-max-tokens').checked;
    const maxTokens = maxTokensEnabled ? parseInt(document.getElementById('max-tokens-slider').value) : null;
    const topP = parseFloat(document.getElementById('top-p-slider').value);
    const topK = parseInt(document.getElementById('top-k-slider').value);
    
    // 2. Setup Assistant Placeholder Bubble
    const assistantMsgId = `assistant-msg-${Date.now()}`;
    appendMessageHTML('assistant', '', assistantMsgId);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    const bubbleTextEl = document.querySelector(`#${assistantMsgId} .message-text`);
    bubbleTextEl.classList.add('typing-cursor');
    
    // Toggle actions buttons
    const stopBtn = document.getElementById('btn-stop-generation');
    const sendBtn = document.getElementById('btn-send-message');
    stopBtn.classList.remove('hidden');
    sendBtn.disabled = true;
    
    // Prepare API call
    activeStreamController = new AbortController();
    const historyPayload = chatHistory.map(m => ({ role: m.role, content: m.content }));
    
    let accumulatedText = "";
    const startTime = Date.now();
    
    // Typewriter animation queue state
    let textQueue = [];
    let typedText = "";
    let streamDone = false;
    let finalDonePayload = null;
    let typewriterActive = true;
    
    // Smooth character-by-character typewriter animation loop
    const typewriterInterval = setInterval(() => {
        if (!typewriterActive) {
            clearInterval(typewriterInterval);
            return;
        }
        
        if (textQueue.length > 0) {
            // Speed up typing if queue gets backlogged to stay responsive
            let charsToType = 1;
            if (textQueue.length > 100) charsToType = 4;
            else if (textQueue.length > 30) charsToType = 2;
            
            for (let i = 0; i < charsToType && textQueue.length > 0; i++) {
                typedText += textQueue.shift();
            }
            bubbleTextEl.textContent = typedText;
            messagesArea.scrollTop = messagesArea.scrollHeight;
        } else if (streamDone) {
            clearInterval(typewriterInterval);
            bubbleTextEl.classList.remove('typing-cursor');
            
            if (finalDonePayload) {
                const durationMs = Date.now() - startTime;
                const tokenCount = finalDonePayload.tokens.length;
                const speed = durationMs > 0 ? ((tokenCount / durationMs) * 1000).toFixed(1) : 0;
                
                // Render stats footer in message bubble
                renderMessageFooter(assistantMsgId, tokenCount, durationMs, speed, finalDonePayload.tokens);
                
                // Update session token counters
                sessionPromptTokens += finalDonePayload.usage.prompt_tokens;
                sessionCompletionTokens += finalDonePayload.usage.completion_tokens;
                sessionTotalTokens += finalDonePayload.usage.total_tokens;
                updateSessionProgress();
                
                // Save in chat history
                chatHistory.push({ role: 'user', content: userMsg });
                chatHistory.push({ role: 'assistant', content: typedText });
                
                // Check if model hit token limits
                if (finalDonePayload.finish_reason === 'MAX_TOKENS' || finalDonePayload.finish_reason === 'MAX_OUTPUT_TOKENS') {
                    showCutoffWarning(maxTokens);
                }
            }
            
            document.getElementById('btn-stop-generation').classList.add('hidden');
            document.getElementById('btn-send-message').disabled = false;
        }
    }, 15);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMsg,
                history: historyPayload,
                model: model,
                temperature: temp,
                max_output_tokens: maxTokens,
                top_p: topP,
                top_k: topK
            }),
            signal: activeStreamController.signal
        });
        
        if (!response.ok) {
            throw new Error(`Server returned error: ${response.statusText}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6).trim();
                    if (!dataStr) continue;
                    
                    const payload = JSON.parse(dataStr);
                    
                    if (payload.type === 'chunk') {
                        accumulatedText += payload.text;
                        // Queue incoming characters for smooth typewriter output
                        for (let char of payload.text) {
                            textQueue.push(char);
                        }
                    } else if (payload.type === 'done') {
                        finalDonePayload = payload;
                        streamDone = true;
                    } else if (payload.type === 'error') {
                        throw new Error(payload.message);
                    }
                }
            }
        }
    } catch (err) {
        typewriterActive = false;
        clearInterval(typewriterInterval);
        
        if (err.name === 'AbortError') {
            bubbleTextEl.classList.remove('typing-cursor');
            // Instantly dump remaining queue content if generation was aborted
            const remaining = textQueue.join('');
            typedText += remaining;
            bubbleTextEl.textContent = typedText + " [Generation Stopped]";
            chatHistory.push({ role: 'user', content: userMsg });
            chatHistory.push({ role: 'assistant', content: typedText });
        } else {
            console.error("[ERROR]", err);
            bubbleTextEl.classList.remove('typing-cursor');
            bubbleTextEl.innerHTML = `<span style="color:#ef4444; font-weight:500;">⚠ Request Failed:</span> ${err.message}`;
        }
    } finally {
        activeStreamController = null;
        if (streamDone || !typewriterActive) {
            document.getElementById('btn-stop-generation').classList.add('hidden');
            document.getElementById('btn-send-message').disabled = false;
        }
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

// Stop current SSE stream
function stopGeneration() {
    if (activeStreamController) {
        activeStreamController.abort();
    }
}

// Append visual message bubble to chat window
function appendMessageHTML(role, text, customId = null) {
    const area = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    if (customId) msgDiv.id = customId;
    
    const senderName = role === 'user' ? 'User' : 'Gemini Studio';
    
    msgDiv.innerHTML = `
        <span class="message-sender">${senderName}</span>
        <div class="message-bubble-wrapper">
            <div class="message-text">${text}</div>
            <div class="tokenized-view-container">
                <div class="tokenized-view-title">Subword Token Map</div>
                <div class="tokenized-spans"></div>
            </div>
        </div>
    `;
    area.appendChild(msgDiv);
}

// Renders the stats line and sets up visual tokens
function renderMessageFooter(msgId, count, ms, tps, tokens) {
    const bubbleWrapper = document.querySelector(`#${msgId} .message-bubble-wrapper`);
    if (!bubbleWrapper) return;
    
    // Create footer element
    const footer = document.createElement('div');
    footer.className = 'message-footer';
    
    footer.innerHTML = `
        <button class="toggle-token-btn" onclick="toggleTokenView('${msgId}')">View Tokens</button>
        <div class="message-stats">
            <span>${count} tokens</span>
            <span>${(ms/1000).toFixed(2)}s</span>
            <span>${tps} t/s</span>
        </div>
    `;
    bubbleWrapper.appendChild(footer);
    
    // Fill the tokenized-spans container for toggle view
    const spanContainer = document.querySelector(`#${msgId} .tokenized-spans`);
    if (spanContainer && tokens) {
        renderTokensToContainer(tokens, spanContainer);
    }
}

// Toggles visual token map in chat
function toggleTokenView(msgId) {
    const tokenContainer = document.querySelector(`#${msgId} .tokenized-view-container`);
    const toggleBtn = document.querySelector(`#${msgId} .toggle-token-btn`);
    if (tokenContainer) {
        const isActive = tokenContainer.classList.toggle('active');
        toggleBtn.textContent = isActive ? 'Hide Tokens' : 'View Tokens';
    }
}

// Renders list of token objects as styled span badges
function renderTokensToContainer(tokens, container) {
    container.innerHTML = '';
    
    if (!tokens || tokens.length === 0) {
        container.innerHTML = '<span class="placeholder-text">Empty tokens</span>';
        return;
    }
    
    tokens.forEach(token => {
        const span = document.createElement('span');
        span.className = `token-span token-c-${token.color_index}`;
        span.title = `Token ID: ${token.id}`;
        
        // Replace spaces with visible whitespace indicator if the token is only space
        if (token.text === ' ') {
            span.textContent = ' '; // standard space, css preserves it
        } else {
            span.textContent = token.text;
        }
        
        container.appendChild(span);
    });
}

// Tab 2: Handle live typing tokenization
let tokenizerDebounceTimer = null;
function handleTokenizerInput() {
    clearTimeout(tokenizerDebounceTimer);
    
    // Debounce to avoid flooding the backend with every keystroke
    tokenizerDebounceTimer = setTimeout(async () => {
        const text = document.getElementById('tokenizer-input-text').value;
        const outputView = document.getElementById('tokenized-output-view');
        
        if (!text) {
            outputView.innerHTML = '<span class="placeholder-text">Tokens will appear here as you type...</span>';
            updateTokenizerMetrics(0, 0, 0);
            updateTokenTable([]);
            return;
        }
        
        try {
            const response = await fetch('/api/tokenize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // 1. Render Visual Spans
                renderTokensToContainer(data.tokens, outputView);
                
                // 2. Update stats bar
                const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
                updateTokenizerMetrics(data.count, text.length, wordCount);
                
                // 3. Update table map
                updateTokenTable(data.tokens);
            }
        } catch (err) {
            console.error("Tokenization error:", err);
            outputView.innerHTML = `<span style="color:#ef4444;">Failed to connect to tokenizer service: ${err.message}</span>`;
        }
    }, 150);
}

// Update live tokenizer panel metrics
function updateTokenizerMetrics(tokens, chars, words) {
    document.getElementById('token-count-num').textContent = tokens;
    document.getElementById('char-count-num').textContent = chars;
    document.getElementById('word-count-num').textContent = words;
    
    const cpt = tokens > 0 ? (chars / tokens).toFixed(1) : '0.0';
    document.getElementById('chars-per-token-num').textContent = cpt;
}

// Update table listing token detail hashes
function updateTokenTable(tokens) {
    const tbody = document.getElementById('token-table-body');
    tbody.innerHTML = '';
    
    if (!tokens || tokens.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="table-placeholder">No tokenized data available</td></tr>';
        return;
    }
    
    // Limit displaying table rows to prevent lag on huge texts (limit to 100 rows)
    const limitTokens = tokens.slice(0, 100);
    
    limitTokens.forEach((token, idx) => {
        const row = document.createElement('tr');
        
        // Escape space character representation for visual clarity in table
        let fragmentText = token.text;
        if (fragmentText === '\n') {
            fragmentText = '\\n (Newline)';
        } else if (fragmentText.isspace) {
            fragmentText = `\\s (Whitespace x${fragmentText.length})`;
        } else if (fragmentText === ' ') {
            fragmentText = '\u2420 (Space)';
        }
        
        row.innerHTML = `
            <td><code>${escapeHTML(fragmentText)}</code></td>
            <td><code>${token.id}</code></td>
            <td><span class="token-span token-c-${token.color_index}" style="padding: 2px 10px; margin: 0; font-size:11px;">Color Index ${token.color_index}</span></td>
        `;
        tbody.appendChild(row);
    });
    
    if (tokens.length > 100) {
        const footerRow = document.createElement('tr');
        footerRow.innerHTML = `<td colspan="3" class="table-placeholder">Showing first 100 of ${tokens.length} tokens...</td>`;
        tbody.appendChild(footerRow);
    }
}

// Helper: Escape HTML strings to prevent XSS
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
