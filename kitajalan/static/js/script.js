// script.js

// ===============================
// FUNGSI GET MATERI
// ===============================

function getMateri(pk) {
    fetch(`/get_materi/${pk}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Data:', data);
            
            const materiKursus = document.getElementById('materi-kursus');
            if (!materiKursus) return;
            
            materiKursus.innerHTML = '';
            
            data.forEach(materi => {
                console.log('Materi:', materi);
                
                const li = document.createElement('li');
                const a = document.createElement('a');
                
                // Buat slug dari konten
                const slug = materi.konten
                    .replace(/[^a-zA-Z0-9]+/g, '-')
                    .replace(/^-+|-+$/g, '')
                    .toLowerCase();
                
                a.href = `${slug}.html`;
                a.textContent = materi.konten;
                
                li.appendChild(a);
                
                const p = document.createElement('p');
                p.textContent = materi.konten;
                
                materiKursus.appendChild(li);
                materiKursus.appendChild(p);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Gagal memuat materi', 'error');
        });
}

// ===============================
// VIDEO ERROR HANDLER (untuk halaman_detail)
// ===============================

function initVideoHandlers() {
    const videoBlocks = document.querySelectorAll('.blok-video iframe');
    
    videoBlocks.forEach(iframe => {
        if (iframe.src.includes('youtube')) {
            
            iframe.addEventListener('error', function() {
                console.log('Video failed to load');
                
                const block = this.closest('.blok-video');
                if (!block) return;
                
                const fallback = block.querySelector('.video-fallback');
                
                if (fallback) {
                    // Hide iframe
                    this.style.display = 'none';
                    
                    // Remove wrapper padding
                    const wrapper = this.closest('.video-wrapper');
                    if (wrapper) {
                        wrapper.style.paddingBottom = '0';
                        wrapper.style.height = 'auto';
                    }
                    
                    // Show fallback
                    fallback.style.display = 'block';
                }
            });
            
            iframe.addEventListener('load', function() {
                console.log('Video loaded successfully');
            });
        }
    });
}

// ===============================
// RETRY VIDEO FUNCTION
// ===============================

function retryVideo(blockId) {
    const block = document.getElementById(`video-block-${blockId}`);
    if (!block) return;
    
    const iframe = block.querySelector('iframe');
    const fallback = block.querySelector('.video-fallback');
    
    if (iframe && fallback) {
        // Show iframe again
        iframe.style.display = 'block';
        
        // Restore wrapper
        const wrapper = iframe.closest('.video-wrapper');
        if (wrapper) {
            wrapper.style.paddingBottom = '56.25%';
            wrapper.style.height = '0';
        }
        
        // Hide fallback
        fallback.style.display = 'none';
        
        // Reload iframe with nocookie domain
        const videoId = iframe.src.split('/').pop().split('?')[0];
        iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&modestbranding=1&iv_load_policy=3&enablejsapi=1`;
    }
}

// ===============================
// NOTIFICATION SYSTEM
// ===============================

function showNotification(message, type = 'info') {
    // Buat element notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Styling
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
    
    // Close button
    notification.querySelector('.notification-close').onclick = () => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    };
}

// ===============================
// PROGRESS TRACKING
// ===============================

function initProgressTracking() {
    const markDoneButtons = document.querySelectorAll('.mark-done-btn');
    
    markDoneButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const halamanId = this.dataset.halamanId;
            const csrftoken = getCookie('csrftoken');
            
            fetch(`/halaman/${halamanId}/selesai/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Progress tersimpan!', 'success');
                    // Update UI
                    this.disabled = true;
                    this.innerHTML = '✓ Selesai';
                    
                    // Update sidebar
                    updateSidebarProgress(halamanId);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Gagal menyimpan progress', 'error');
            });
        });
    });
}

// ===============================
// UTILITY: GET CSRF TOKEN
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
// SIDEBAR PROGRESS UPDATE
// ===============================

function updateSidebarProgress(halamanId) {
    const sidebarItem = document.querySelector(`.sidebar li a[data-halaman-id="${halamanId}"]`);
    if (sidebarItem) {
        const statusIcon = sidebarItem.parentElement.querySelector('.status-icon');
        if (statusIcon) {
            statusIcon.innerHTML = '✔';
            statusIcon.classList.remove('pending');
            statusIcon.classList.add('completed');
        }
    }
}

// ===============================
// INITIALIZE ON PAGE LOAD
// ===============================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize video handlers if on halaman_detail page
    if (document.querySelector('.blok-video')) {
        initVideoHandlers();
    }
    
    // Initialize progress tracking if on materi page
    if (document.querySelector('.mark-done-btn')) {
        initProgressTracking();
    }
    
    console.log('Script.js loaded successfully');
});