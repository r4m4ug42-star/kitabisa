// editor.js

// ===============================
// MARKDOWN EDITOR CONFIGURATION
// ===============================

function initMarkdownEditor() {
    const textarea = document.getElementById("markdown-editor");
    if (!textarea) return null;

    // Load EasyMDE jika belum ada
    if (typeof EasyMDE === 'undefined') {
        console.error('EasyMDE library not loaded');
        return null;
    }

    const easyMDE = new EasyMDE({
        element: textarea,
        spellChecker: false,
        autofocus: true,
        minHeight: "300px",
        maxHeight: "500px",
        placeholder: "Tulis materi kursus dalam format Markdown...",
        status: ["lines", "words", "cursor"],
        
        // Toolbar configuration
        toolbar: [
            "bold", "italic", "heading",
            "|",
            "quote", "code", "table",
            "|",
            {
                name: "info",
                action: function customInfo(editor) {
                    const cm = editor.codemirror;
                    cm.replaceSelection(
`!!! info
    Tulis info di sini
`
                    );
                },
                className: "fa fa-info-circle",
                title: "Info Box"
            },
            {
                name: "warning",
                action: function customWarning(editor) {
                    const cm = editor.codemirror;
                    cm.replaceSelection(
`!!! warning
    Tulis peringatan di sini
`
                    );
                },
                className: "fa fa-exclamation-triangle",
                title: "Warning Box"
            },
            {
                name: "video",
                action: function customVideo(editor) {
                    const cm = editor.codemirror;
                    cm.replaceSelection(
`[![Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://youtu.be/VIDEO_ID)
`
                    );
                },
                className: "fa fa-video",
                title: "Insert Video"
            },
            "|",
            "preview", "side-by-side", "fullscreen"
        ],
        
        // Preview render
        previewRender: function(plainText) {
            // Kirim ke server untuk render markdown
            return previewMarkdown(plainText);
        },
        
        // Shortcuts
        shortcuts: {
            drawTable: "Cmd-Alt-T"
        }
    });

    // Tambahkan custom status bar
    easyMDE.codemirror.on("update", function() {
        const wordCount = easyMDE.value().split(/\s+/).filter(w => w.length > 0).length;
        const charCount = easyMDE.value().length;
        
        const statusBar = document.querySelector('.editor-statusbar');
        if (statusBar) {
            const wordStatus = statusBar.querySelector('.status-word-count');
            if (wordStatus) {
                wordStatus.textContent = `${wordCount} kata`;
            }
        }
    });

    return easyMDE;
}

// ===============================
// PREVIEW MARKDOWN VIA AJAX
// ===============================

function previewMarkdown(text) {
    let result = '<p>Loading preview...</p>';
    
    fetch('/preview-markdown/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `konten=${encodeURIComponent(text)}`
    })
    .then(response => response.json())
    .then(data => {
        result = data.html;
        // Trigger preview update
        const preview = document.querySelector('.editor-preview');
        if (preview) {
            preview.innerHTML = result;
        }
    })
    .catch(error => {
        console.error('Preview error:', error);
        result = '<p class="text-danger">Error loading preview</p>';
    });
    
    return result;
}

// ===============================
// AUTO-SAVE FUNCTIONALITY
// ===============================

function initAutoSave(editor, saveUrl) {
    let saveTimeout;
    
    editor.codemirror.on("change", function() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            saveContent(editor.value(), saveUrl);
        }, 2000); // Auto save after 2 seconds
    });
}

function saveContent(content, saveUrl) {
    fetch(saveUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `content=${encodeURIComponent(content)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveNotification('Tersimpan');
        }
    })
    .catch(error => console.error('Save error:', error));
}

function showSaveNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'auto-save-notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        animation: fadeOut 2s ease;
        z-index: 9999;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 2000);
}

// ===============================
// UTILITY: GET CSRF TOKEN (sama dengan di script.js)
// ===============================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===============================
// INITIALIZE ON PAGE LOAD
// ===============================

document.addEventListener('DOMContentLoaded', function() {
    // Cek apakah ini halaman dengan editor
    if (document.getElementById('markdown-editor')) {
        // Load EasyMDE CSS
        if (!document.querySelector('link[href*="easymde"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://unpkg.com/easymde/dist/easymde.min.css';
            document.head.appendChild(link);
        }
        
        // Load EasyMDE JS
        if (typeof EasyMDE === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/easymde/dist/easymde.min.js';
            script.onload = function() {
                window.easyMDE = initMarkdownEditor();
            };
            document.head.appendChild(script);
        } else {
            window.easyMDE = initMarkdownEditor();
        }
    }
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        0% { opacity: 1; }
        70% { opacity: 1; }
        100% { opacity: 0; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); }
        to { transform: translateX(100%); }
    }
`;
document.head.appendChild(style);