let lastResponseId = null;
let controller = null;
let isGenerating = false;

// Initialize Lucide Icons
lucide.createIcons();

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function handleAction() {
    if (isGenerating) stopGeneration();
    else sendPrompt();
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent adding a new line
        handleAction();
    }
}

function stopGeneration() {
    if (controller) {
        controller.abort();
        isGenerating = false;
        updateUIState(false);
    }
}

function updateUIState(generating) {
    isGenerating = generating;
    const btn = document.getElementById("actionBtn");
    const icon = document.getElementById("buttonIcon");
    const statusText = document.getElementById("status-text");

    if (generating) {
        btn.classList.add("stop-state");
        icon.setAttribute("data-lucide", "square");
        statusText.textContent = "Aura is thinking...";
    } else {
        btn.classList.remove("stop-state");
        icon.setAttribute("data-lucide", "arrow-up");
        statusText.textContent = "System Ready";
    }
    lucide.createIcons();
}

async function sendPrompt() {
    const input = document.getElementById("prompt");
    const chatFlow = document.getElementById("chat-flow");
    const viewport = document.getElementById("chat-viewport");
    const text = input.value.trim();

    if (!text) return;

    updateUIState(true);
    controller = new AbortController();

    // User Message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.textContent = text;
    chatFlow.appendChild(userDiv);

    input.value = "";
    autoResize(input);

    // Bot Message Container
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    chatFlow.appendChild(botDiv);

    let fullText = "";

    try {
        const response = await fetch("http://localhost:8000/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: text }),
            signal: controller.signal
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            fullText += chunk;

            // Handle ID extraction and Markdown rendering
            const cleanText = fullText.replace(/\[ID:(.*?)\]/, (match, id) => {
                lastResponseId = id;
                return "";
            });

            botDiv.innerHTML = marked.parse(cleanText);
            viewport.scrollTop = viewport.scrollHeight;
        }

        renderFeedback(botDiv, lastResponseId);

    } catch (err) {
        if (err.name === 'AbortError') {
            botDiv.innerHTML += "<p><em>Generation halted.</em></p>";
        } else {
            botDiv.innerHTML = "Error: Unable to connect to Aura.";
        }
    } finally {
        updateUIState(false);
    }
}

function renderFeedback(container, id) {
    const fbDiv = document.createElement("div");
    fbDiv.className = "feedback-area";
    fbDiv.id = `fb-container-${id}`;
    fbDiv.innerHTML = `
        <i data-lucide="thumbs-up" class="vote-btn" onclick="castVote('${id}', 'upvote')"></i>
        <i data-lucide="thumbs-down" class="vote-btn" onclick="castVote('${id}', 'downvote')"></i>
    `;
    container.appendChild(fbDiv);
    lucide.createIcons();
}

async function castVote(id, rating) {
    const container = document.getElementById(`fb-container-${id}`);
    container.dataset.rating = rating;
    
    // UI Update: Lock voting
    container.innerHTML = `
        <span class="voted-msg">Feedback received</span>
        <span class="comment-link" onclick="addComment('${id}')">Add note</span>
    `;

    await fetch("http://localhost:8000/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ response_id: id, rating: rating })
    });
}

function addComment(id) {
    const container = document.getElementById(`fb-container-${id}`);
    container.innerHTML = `
        <div style="display:flex; gap:5px; width:100%">
            <input type="text" id="input-${id}" placeholder="Details..." style="flex:1; background:#111; border:1px solid #333; color:white; padding:4px; border-radius:4px; font-size:0.7rem;">
            <button type="button" onclick="saveComment('${id}')" style="width:auto; height:24px; font-size:0.6rem; padding:0 10px;">Save</button>
        </div>
    `;
}

async function saveComment(id) {
    const comment = document.getElementById(`input-${id}`).value;
    const container = document.getElementById(`fb-container-${id}`);
    const rating = container.dataset.rating;
    container.innerHTML = `<span class="voted-msg">Thank you.</span>`;
    
    // Final feedback update
    await fetch("http://localhost:8000/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ response_id: id, rating: rating, comment: comment })
    });
}