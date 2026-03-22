// markdown_preview.js

document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.querySelector("#id_konten");
    if (!textarea) return;

    // ===============================
    // CREATE PREVIEW BUTTON
    // ===============================
    const btn = document.createElement("button");
    btn.type = "button";
    btn.innerText = "Preview Markdown";
    btn.className = "btn-preview-markdown"; // Tambah class untuk styling
    btn.style.cssText = `
        margin: 10px 0;
        padding: 8px 16px;
        background: #2196F3;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.3s;
    `;

    // Hover effect
    btn.addEventListener('mouseover', () => btn.style.background = '#1976D2');
    btn.addEventListener('mouseout', () => btn.style.background = '#2196F3');

    // ===============================
    // CREATE PREVIEW CONTAINER
    // ===============================
    const preview = document.createElement("div");
    preview.className = "markdown-preview-container";
    preview.style.cssText = `
        border: 1px solid #ddd;
        padding: 20px;
        margin-top: 15px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 100px;
        max-height: 600px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    `;

    // Add loading indicator
    const loadingIndicator = document.createElement("div");
    loadingIndicator.className = "preview-loading";
    loadingIndicator.style.cssText = `
        display: none;
        text-align: center;
        padding: 40px;
        color: #666;
    `;
    loadingIndicator.innerHTML = `
        <div class="spinner" style="
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        "></div>
        <p>Memuat preview...</p>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    preview.appendChild(loadingIndicator);

    // ===============================
    // ADD ELEMENTS TO DOM
    // ===============================
    textarea.parentNode.appendChild(btn);
    textarea.parentNode.appendChild(preview);

    // ===============================
    // PREVIEW FUNCTION
    // ===============================
    async function fetchMarkdownPreview(content) {
        try {
            const response = await fetch("/preview-markdown/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    konten: content
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.html;
        } catch (error) {
            console.error('Preview error:', error);
            return '<p class="text-danger">Error loading preview. Please try again.</p>';
        }
    }

    // ===============================
    // HANDLE PREVIEW BUTTON CLICK
    // ===============================
    btn.addEventListener("click", async function () {
        // Show loading
        preview.querySelector('.markdown-preview').style.display = 'none';
        loadingIndicator.style.display = 'block';
        
        // Disable button while loading
        btn.disabled = true;
        btn.style.opacity = '0.6';
        btn.style.cursor = 'not-allowed';

        try {
            const html = await fetchMarkdownPreview(textarea.value);
            
            // Create or update content div
            let contentDiv = preview.querySelector('.markdown-preview');
            if (!contentDiv) {
                contentDiv = document.createElement('div');
                contentDiv.className = 'markdown-preview lesson-content'; // Add lesson-content class for styling
                preview.appendChild(contentDiv);
            }
            
            contentDiv.innerHTML = html;
            contentDiv.style.display = 'block';
            
            // Hide loading
            loadingIndicator.style.display = 'none';
            
            // Apply syntax highlighting if Pygments is used
            if (window.hljs) {
                contentDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            }
            
        } catch (error) {
            console.error('Preview error:', error);
            
            // Show error message
            let contentDiv = preview.querySelector('.markdown-preview');
            if (!contentDiv) {
                contentDiv = document.createElement('div');
                contentDiv.className = 'markdown-preview';
                preview.appendChild(contentDiv);
            }
            contentDiv.innerHTML = '<p class="text-danger">Gagal memuat preview. Silakan coba lagi.</p>';
            contentDiv.style.display = 'block';
            
        } finally {
            // Re-enable button
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.style.cursor = 'pointer';
            loadingIndicator.style.display = 'none';
        }
    });

    // ===============================
    // OPTIONAL: AUTO-PREVIEW ON TYPING (dengan debounce)
    // ===============================
    let previewTimeout;
    textarea.addEventListener('input', function() {
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(() => {
            // Auto preview after 2 seconds of no typing
            if (confirm('Auto-preview? Click OK to see preview')) {
                btn.click();
            }
        }, 2000);
    });

    // ===============================
    // ADD KEYBOARD SHORTCUT (Ctrl+Shift+P)
    // ===============================
    textarea.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'P') {
            e.preventDefault();
            btn.click();
        }
    });
});