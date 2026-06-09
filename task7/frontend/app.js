// Frontend Logic for Gemini RAG Studio
let chatHistory = [];
let activeTab = 'chat';
let activeStreamController = null;

// Session token counters
let sessionPromptTokens = 0;
let sessionCompletionTokens = 0;
let sessionTotalTokens = 0;
const SESSION_LIMIT = 5000;

// Initialize UI elements when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupSliders();
    setupTextareaAutoHeight();
    setupRAGToggle();
    setupFileUpload();
    refreshKBStatus();
});

// ─── Tab Switching ──────────────────────────────────────────────────────────

function switchTab(tabName) {
    activeTab = tabName;
    
    document.getElementById('nav-chat-tab').classList.toggle('active', tabName === 'chat');
    document.getElementById('nav-knowledge-tab').classList.toggle('active', tabName === 'knowledge');
    
    document.getElementById('tab-chat').classList.toggle('workspace-tabactive', tabName === 'chat');
    document.getElementById('tab-knowledge').classList.toggle('workspace-tabactive', tabName === 'knowledge');

    // Refresh KB status when switching to knowledge tab
    if (tabName === 'knowledge') {
        refreshKBStatus();
    }
}

// ─── Slider Setup ───────────────────────────────────────────────────────────

function setupSliders() {
    const sliders = [
        { id: 'temperature-slider', valId: 'temperature-value', fix: 2 },
        { id: 'top-p-slider', valId: 'top-p-value', fix: 2 },
        { id: 'top-k-slider', valId: 'top-k-value', fix: 0 },
        { id: 'rag-topk-slider', valId: 'rag-topk-value', fix: 0 }
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

// ─── RAG Toggle ─────────────────────────────────────────────────────────────

function setupRAGToggle() {
    const enableRAG = document.getElementById('enable-rag');
    const badge = document.getElementById('rag-status-badge');
    const topkGroup = document.getElementById('rag-topk-group');

    if (enableRAG) {
        enableRAG.addEventListener('change', () => {
            const on = enableRAG.checked;
            badge.textContent = on ? 'ON' : 'OFF';
            badge.classList.toggle('rag-on', on);
            badge.classList.toggle('rag-off', !on);
            topkGroup.style.opacity = on ? '1' : '0.35';
            topkGroup.style.pointerEvents = on ? 'auto' : 'none';
        });
    }
}

// ─── Textarea Auto-height ───────────────────────────────────────────────────

function setupTextareaAutoHeight() {
    const tx = document.getElementById('chat-input');
    if (tx) {
        tx.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight - 4) + 'px';
        });
        
        tx.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                document.getElementById('chat-form').requestSubmit();
            }
        });
    }
}

// ─── Warning Banner ─────────────────────────────────────────────────────────

function showCutoffWarning(limit) {
    const banner = document.getElementById('cutoff-warning-banner');
    const msgText = document.getElementById('warning-message-text');
    msgText.textContent = `The response was cut off because it reached the Max Output Tokens limit of ${limit} tokens.`;
    banner.classList.remove('hidden');
}

function dismissWarning() {
    document.getElementById('cutoff-warning-banner').classList.add('hidden');
}

// ─── Session Progress ───────────────────────────────────────────────────────

function updateSessionProgress() {
    const promptEl = document.getElementById('session-prompt-tokens');
    if (promptEl) promptEl.textContent = sessionPromptTokens;
    const completionEl = document.getElementById('session-completion-tokens');
    if (completionEl) completionEl.textContent = sessionCompletionTokens;
    const totalEl = document.getElementById('session-total-tokens');
    if (totalEl) totalEl.textContent = sessionTotalTokens;

    const percent = Math.min(100, Math.round((sessionTotalTokens / SESSION_LIMIT) * 100));
    const percentEl = document.getElementById('progress-percent');
    if (percentEl) percentEl.textContent = percent;
    
    const fill = document.getElementById('progress-fill');
    if (fill) {
        fill.style.width = `${percent}%`;
        if (percent > 85) {
            fill.style.background = 'linear-gradient(to right, #f43f5e, #e11d48)';
        } else if (percent > 60) {
            fill.style.background = 'linear-gradient(to right, #eab308, #ca8a04)';
        } else {
            fill.style.background = 'linear-gradient(to right, var(--primary), var(--secondary))';
        }
    }
}

// ─── Clear Session ──────────────────────────────────────────────────────────

function clearChatHistory() {
    chatHistory = [];
    sessionPromptTokens = 0;
    sessionCompletionTokens = 0;
    sessionTotalTokens = 0;
    updateSessionProgress();
    dismissWarning();
    
    const area = document.getElementById('chat-messages');
    area.innerHTML = `
        <div class="welcome-box" id="welcome-message">
            <div class="welcome-gemini-gradient"></div>
            <h2>Welcome to Gemini RAG Studio</h2>
            <p>This interactive chat environment demonstrates <strong>Retrieval-Augmented Generation (RAG)</strong>, <strong>Tokenization</strong>, and <strong>Generation Limits</strong>. Upload documents to the Knowledge Base, enable RAG, and ask questions grounded in your own data.</p>
            <div class="welcome-features">
                <div class="feature-card">
                    <h3>📚 RAG Pipeline</h3>
                    <p>Upload documents, chunk & embed them, then retrieve relevant context before generating responses.</p>
                </div>
                <div class="feature-card">
                    <h3>💡 Streaming Tokens</h3>
                    <p>Watch responses generate segment by segment in real-time, just like Gemini.</p>
                </div>
                <div class="feature-card">
                    <h3>🎨 Visual Tokenizer</h3>
                    <p>Toggle <strong>"View Tokens"</strong> on any response to see subword tokenization.</p>
                </div>
            </div>
        </div>
    `;
}

// ─── Chat Submission ────────────────────────────────────────────────────────

async function handleChatSubmit(event) {
    event.preventDefault();
    
    const inputEl = document.getElementById('chat-input');
    // Submit on Enter (without Shift); allow Shift+Enter for newline
    inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('chat-form').requestSubmit();
        }
    });
    const userMsg = inputEl.value.trim();
    if (!userMsg) return;
    
    inputEl.value = '';
    inputEl.style.height = 'auto';
    dismissWarning();
    
    const welcome = document.getElementById('welcome-message');
    if (welcome) welcome.remove();
    
    const messagesArea = document.getElementById('chat-messages');
    
    // Render User Message
    appendMessageHTML('user', userMsg);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    // Grab configuration
    const model = 'gemini-2.5-flash'; // default model
    const temp = 0.7; // default temperature
    const maxTokens = null; // no token limit
    const topP = 0.95; // default top-p
    const topK = 40; // default top-k
    const useRAG = false; // RAG disabled
    const ragTopK = 5; // default RAG top K
    
    // Setup Assistant Placeholder
    const assistantMsgId = `assistant-msg-${Date.now()}`;
    appendMessageHTML('assistant', '', assistantMsgId);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    const bubbleTextEl = document.querySelector(`#${assistantMsgId} .message-text`);
    bubbleTextEl.classList.add('typing-cursor');
    
    const stopBtn = document.getElementById('btn-stop-generation');
    const sendBtn = document.getElementById('btn-send-message');
    stopBtn.classList.remove('hidden');
    sendBtn.disabled = true;
    
    activeStreamController = new AbortController();
    const historyPayload = chatHistory.map(m => ({ role: m.role, content: m.content }));
    
    let accumulatedText = "";
    const startTime = Date.now();
    
    // Typewriter animation
    let textQueue = [];
    let typedText = "";
    let streamDone = false;
    let finalDonePayload = null;
    let typewriterActive = true;
    let ragChunksReceived = [];
    
    const typewriterInterval = setInterval(() => {
        if (!typewriterActive) {
            clearInterval(typewriterInterval);
            return;
        }
        
        if (textQueue.length > 0) {
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
                
                renderMessageFooter(assistantMsgId, tokenCount, durationMs, speed, finalDonePayload.tokens, ragChunksReceived);
                
                sessionPromptTokens += finalDonePayload.usage.prompt_tokens;
                sessionCompletionTokens += finalDonePayload.usage.completion_tokens;
                sessionTotalTokens += finalDonePayload.usage.total_tokens;
                updateSessionProgress();
                
                chatHistory.push({ role: 'user', content: userMsg });
                chatHistory.push({ role: 'assistant', content: typedText });
                
                if (finalDonePayload.finish_reason === 'MAX_TOKENS' || finalDonePayload.finish_reason === 'MAX_OUTPUT_TOKENS') {
                    showCutoffWarning(maxTokens);
                }
            }
            
            document.getElementById('btn-stop-generation').classList.add('hidden');
            document.getElementById('btn-send-message').disabled = false;
        }
    }, 15);
    
    try {
        const response = await fetch('http://127.0.0.1:8001/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMsg,
                history: historyPayload,
                model: model,
                temperature: temp,
                max_output_tokens: maxTokens,
                top_p: topP,
                top_k: topK,
                use_rag: useRAG,
                rag_top_k: ragTopK
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
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6).trim();
                    if (!dataStr) continue;
                    
                    const payload = JSON.parse(dataStr);
                    
                    if (payload.type === 'rag_context') {
                        // Show RAG sources indicator on the message
                        ragChunksReceived = payload.chunks || [];
                        if (ragChunksReceived.length > 0) {
                            renderRAGSourcesBadge(assistantMsgId, ragChunksReceived);
                        }
                    } else if (payload.type === 'chunk') {
                        accumulatedText += payload.text;
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

// ─── Stop Generation ────────────────────────────────────────────────────────

function stopGeneration() {
    if (activeStreamController) {
        activeStreamController.abort();
    }
}

// ─── Message Rendering ──────────────────────────────────────────────────────

function appendMessageHTML(role, text, customId = null) {
    const area = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    if (customId) msgDiv.id = customId;
    
    const senderName = role === 'user' ? 'User' : 'Gemini RAG Studio';
    
    msgDiv.innerHTML = `
        <span class="message-sender">${senderName}</span>
        <div class="message-bubble-wrapper">
            <div class="rag-sources-container"></div>
            <div class="message-text">${text}</div>
            <div class="tokenized-view-container">
                <div class="tokenized-view-title">Subword Token Map</div>
                <div class="tokenized-spans"></div>
            </div>
        </div>
    `;
    area.appendChild(msgDiv);
}

function renderRAGSourcesBadge(msgId, chunks) {
    const container = document.querySelector(`#${msgId} .rag-sources-container`);
    if (!container || chunks.length === 0) return;

    const sources = [...new Set(chunks.map(c => c.source))];
    
    container.innerHTML = `
        <div class="rag-sources-badge">
            <span class="rag-badge-icon">📚</span>
            <span>RAG: ${chunks.length} chunks from ${sources.length} source${sources.length > 1 ? 's' : ''}</span>
            <button class="rag-sources-toggle" onclick="toggleRAGSources('${msgId}')">Show Sources</button>
        </div>
        <div class="rag-sources-detail hidden" id="rag-detail-${msgId}">
            ${chunks.map((c, i) => `
                <div class="rag-chunk-card">
                    <div class="rag-chunk-header">
                        <span class="rag-chunk-source">${escapeHTML(c.source)}</span>
                        <span class="rag-chunk-score">Score: ${c.score.toFixed(3)}</span>
                    </div>
                    <p class="rag-chunk-text">${escapeHTML(c.text.substring(0, 200))}${c.text.length > 200 ? '...' : ''}</p>
                </div>
            `).join('')}
        </div>
    `;
}

function toggleRAGSources(msgId) {
    const detail = document.getElementById(`rag-detail-${msgId}`);
    const btn = document.querySelector(`#${msgId} .rag-sources-toggle`);
    if (detail) {
        const isHidden = detail.classList.toggle('hidden');
        btn.textContent = isHidden ? 'Show Sources' : 'Hide Sources';
    }
}

function renderMessageFooter(msgId, count, ms, tps, tokens, ragChunks) {
    const bubbleWrapper = document.querySelector(`#${msgId} .message-bubble-wrapper`);
    if (!bubbleWrapper) return;
    
    const footer = document.createElement('div');
    footer.className = 'message-footer';
    
    const ragLabel = ragChunks && ragChunks.length > 0 
        ? `<span class="rag-indicator">📚 RAG</span>` 
        : '';
    
    footer.innerHTML = `
        <button class="toggle-token-btn" onclick="toggleTokenView('${msgId}')">View Tokens</button>
        <div class="message-stats">
            ${ragLabel}
            <span>${count} tokens</span>
            <span>${(ms/1000).toFixed(2)}s</span>
            <span>${tps} t/s</span>
        </div>
    `;
    bubbleWrapper.appendChild(footer);
    
    const spanContainer = document.querySelector(`#${msgId} .tokenized-spans`);
    if (spanContainer && tokens) {
        renderTokensToContainer(tokens, spanContainer);
    }
}

// Live Tokenizer functionality has been removed as UI is no longer present.
// The following functions are retained as no-ops to keep code stability.
function toggleTokenView(msgId) {
    // No token view available.
}
function renderTokensToContainer(tokens, container) {
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
                renderTokensToContainer(data.tokens, outputView);
                const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
                updateTokenizerMetrics(data.count, text.length, wordCount);
                updateTokenTable(data.tokens);
            }
        } catch (err) {
            console.error("Tokenization error:", err);
            outputView.innerHTML = `<span style="color:#ef4444;">Failed to connect to tokenizer service: ${err.message}</span>`;
        }
    }, 150);
}

function updateTokenizerMetrics(tokens, chars, words) {
    document.getElementById('token-count-num').textContent = tokens;
    document.getElementById('char-count-num').textContent = chars;
    document.getElementById('word-count-num').textContent = words;
    
    const cpt = tokens > 0 ? (chars / tokens).toFixed(1) : '0.0';
    document.getElementById('chars-per-token-num').textContent = cpt;
}

function updateTokenTable(tokens) {
    const tbody = document.getElementById('token-table-body');
    tbody.innerHTML = '';
    
    if (!tokens || tokens.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="table-placeholder">No tokenized data available</td></tr>';
        return;
    }
    
    const limitTokens = tokens.slice(0, 100);
    
    limitTokens.forEach((token, idx) => {
        const row = document.createElement('tr');
        
        let fragmentText = token.text;
        if (fragmentText === '\n') {
            fragmentText = '\\n (Newline)';
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

// ─── Knowledge Base (Tab 3) ─────────────────────────────────────────────────

function setupFileUpload() {
    const dropZone = document.getElementById('kb-drop-zone');
    const fileInput = document.getElementById('kb-file-input');

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFiles(files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadFiles(fileInput.files);
            fileInput.value = ''; // reset so same file can be re-uploaded
        }
    });
}

async function uploadFiles(files) {
    const dropZone = document.getElementById('kb-drop-zone');
    const originalHTML = dropZone.innerHTML;
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        dropZone.innerHTML = `
            <div class="upload-progress">
                <div class="upload-spinner"></div>
                <p>Ingesting: ${escapeHTML(file.name)} (${i+1}/${files.length})</p>
            </div>
        `;

        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch('/api/ingest/file', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || res.statusText);
            }

            const result = await res.json();
            console.log(`[KB] Ingested ${file.name}:`, result);
        } catch (err) {
            console.error(`[KB] Failed to ingest ${file.name}:`, err);
            alert(`Failed to ingest ${file.name}: ${err.message}`);
        }
    }

    dropZone.innerHTML = originalHTML;
    // Re-attach click handler
    const fileInput = document.getElementById('kb-file-input');
    dropZone.addEventListener('click', () => fileInput.click());
    
    refreshKBStatus();
}

async function handlePasteIngest() {
    const textArea = document.getElementById('kb-paste-text');
    const sourceInput = document.getElementById('kb-paste-source');
    const text = textArea.value.trim();
    const source = sourceInput.value.trim() || 'pasted-text';

    if (!text) {
        alert('Please paste some text first.');
        return;
    }

    const btn = document.getElementById('btn-ingest-paste');
    btn.textContent = 'Ingesting...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/ingest/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, source })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || res.statusText);
        }

        const result = await res.json();
        console.log('[KB] Ingested text:', result);
        textArea.value = '';
        sourceInput.value = '';
        refreshKBStatus();
    } catch (err) {
        console.error('[KB] Ingest error:', err);
        alert(`Ingest failed: ${err.message}`);
    } finally {
        btn.textContent = 'Ingest Text';
        btn.disabled = false;
    }
}

async function refreshKBStatus() {
    try {
        const res = await fetch('/api/rag/status');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('kb-doc-count').textContent = data.total_documents;
        document.getElementById('kb-chunk-count').textContent = data.total_chunks;
        document.getElementById('kb-index-size').textContent = data.index_size;

        const list = document.getElementById('kb-doc-list');
        if (data.documents && data.documents.length > 0) {
            list.innerHTML = data.documents.map((doc, i) => `
                <div class="kb-doc-card">
                    <div class="kb-doc-icon">📄</div>
                    <div class="kb-doc-info">
                        <span class="kb-doc-name">${escapeHTML(doc.source)}</span>
                        <span class="kb-doc-meta">${doc.chunks} chunks · ${doc.chars.toLocaleString()} chars</span>
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = `
                <div class="kb-empty-state">
                    <span class="kb-empty-icon">📭</span>
                    <p>No documents indexed yet</p>
                    <span class="range-hint">Upload files or paste text to get started</span>
                </div>
            `;
        }
    } catch (err) {
        console.error('[KB] Status refresh error:', err);
    }
}

async function handleClearIndex() {
    if (!confirm('Clear the entire Knowledge Base? This cannot be undone.')) return;

    try {
        const res = await fetch('/api/rag/clear', { method: 'POST' });
        if (res.ok) {
            refreshKBStatus();
        }
    } catch (err) {
        console.error('[KB] Clear error:', err);
    }
}

async function handleTestRetrieval() {
    const query = document.getElementById('kb-test-query').value.trim();
    const resultsDiv = document.getElementById('kb-test-results');

    if (!query) {
        alert('Please enter a test query.');
        return;
    }

    resultsDiv.innerHTML = '<span class="placeholder-text">Searching...</span>';

    try {
        const res = await fetch('/api/rag/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, top_k: 5 })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || res.statusText);
        }

        const data = await res.json();

        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = '<span class="placeholder-text">No matching chunks found. Try ingesting documents first.</span>';
            return;
        }

        resultsDiv.innerHTML = data.results.map((hit, i) => `
            <div class="kb-result-card">
                <div class="kb-result-header">
                    <span class="kb-result-rank">#${i + 1}</span>
                    <span class="kb-result-source">${escapeHTML(hit.source)}</span>
                    <span class="kb-result-score">Distance: ${hit.score.toFixed(4)}</span>
                </div>
                <p class="kb-result-text">${escapeHTML(hit.text)}</p>
            </div>
        `).join('');
    } catch (err) {
        console.error('[KB] Query error:', err);
        resultsDiv.innerHTML = `<span style="color:#ef4444;">Retrieval failed: ${err.message}</span>`;
    }
}

// ─── Helper: Escape HTML ────────────────────────────────────────────────────

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
// Global Enter key handler for chat input
document.addEventListener('DOMContentLoaded', () => {
    const inputEl = document.getElementById('chat-input');
    if (inputEl) {
        inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                // Directly invoke the chat submission handler
                // Pass a synthetic event compatible with handleChatSubmit
                handleChatSubmit(e);
            }
        });
    }
});
