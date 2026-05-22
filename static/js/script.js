// SmartShop JavaScript

document.addEventListener('DOMContentLoaded', function() {

    // Mobile nav toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    if (navToggle) navToggle.addEventListener('click', function() { navMenu.classList.toggle('active'); });

    // Smooth scroll for Shop Now
    const shopNowBtn = document.getElementById('shopNowBtn');
    if (shopNowBtn) shopNowBtn.addEventListener('click', function(e) {
        e.preventDefault();
        var t = document.querySelector('#products');
        if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    // Add to Cart confirmation
    document.querySelectorAll('.add-to-cart-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var link = e.target.closest('a');
            if (link && confirm('Add this product to your cart?')) window.location.href = link.getAttribute('href');
        });
    });

    // Remove from cart confirmation
    document.querySelectorAll('.remove-item-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var link = e.target.closest('a');
            if (link && confirm('Remove this item from your cart?')) window.location.href = link.getAttribute('href');
        });
    });

    // ===== HERO BUBBLES MOUSE PARALLAX =====
    var heroSection = document.getElementById('hero');
    var heroBubbles = document.getElementById('heroBubbles');
    if (heroSection && heroBubbles) {
        var shapes = heroBubbles.querySelectorAll('.shape');
        var mouseX = 0, mouseY = 0;
        var currentX = 0, currentY = 0;

        heroSection.addEventListener('mousemove', function(e) {
            var rect = heroSection.getBoundingClientRect();
            // Normalize mouse position to center (-1 to 1)
            mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
            mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
        });

        heroSection.addEventListener('mouseleave', function() {
            mouseX = 0;
            mouseY = 0;
        });

        function animateBubbles() {
            // Smooth interpolation for fluid movement
            currentX += (mouseX - currentX) * 0.08;
            currentY += (mouseY - currentY) * 0.08;

            shapes.forEach(function(shape) {
                var speed = parseFloat(shape.getAttribute('data-speed')) || 0.03;
                var moveX = currentX * speed * 800;
                var moveY = currentY * speed * 600;
                shape.style.transform = 'translate(' + moveX + 'px, ' + moveY + 'px)';
            });

            requestAnimationFrame(animateBubbles);
        }
        animateBubbles();
    }

    // Toast auto-dismiss
    document.querySelectorAll('.toast').forEach(function(t) {
        setTimeout(function() { t.style.transition = 'all 0.5s ease'; t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; setTimeout(function() { t.remove(); }, 500); }, 5000);
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        var nb = document.getElementById('navbar');
        if (nb) nb.style.boxShadow = window.scrollY > 50 ? '0 4px 20px rgba(0,0,0,0.3)' : 'none';
    });

    // ===== DARK/LIGHT MODE =====
    var themeBtn = document.getElementById('themeToggle');
    var themeIcon = document.getElementById('themeIcon');
    var html = document.documentElement;
    var saved = localStorage.getItem('smartshop-theme') || 'dark';
    html.setAttribute('data-theme', saved);
    if (themeIcon) themeIcon.className = saved === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    if (themeBtn) themeBtn.addEventListener('click', function() {
        var cur = html.getAttribute('data-theme');
        var next = cur === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('smartshop-theme', next);
        if (themeIcon) themeIcon.className = next === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    });

    // ===== IMAGE ZOOM =====
    document.querySelectorAll('.zoomable-img').forEach(function(img) {
        img.addEventListener('click', function() {
            var overlay = document.createElement('div');
            overlay.className = 'img-zoom-overlay';
            var zoomed = document.createElement('img');
            zoomed.src = img.src;
            overlay.appendChild(zoomed);
            document.body.appendChild(overlay);
            overlay.addEventListener('click', function() { overlay.remove(); });
        });
    });

    // ===== SCROLL ANIMATIONS =====
    var animEls = document.querySelectorAll('.animate-fadeInUp');
    if (animEls.length > 0) {
        var obs = new IntersectionObserver(function(entries) {
            entries.forEach(function(e) { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
        }, { threshold: 0.1 });
        animEls.forEach(function(el) { obs.observe(el); });
    }

    // ===== AI CHATBOT =====
    var chatToggle = document.getElementById('chatbotToggle');
    var chatWindow = document.getElementById('chatbotWindow');
    var chatClose = document.getElementById('chatbotClose');
    var chatInput = document.getElementById('chatbotInput');
    var chatSend = document.getElementById('chatbotSend');
    var chatMessages = document.getElementById('chatbotMessages');

    if (chatToggle && chatWindow) {
        chatToggle.addEventListener('click', function() {
            chatWindow.classList.toggle('active');
            if (chatWindow.classList.contains('active')) { chatInput.focus(); scrollChat(); }
        });
        chatClose.addEventListener('click', function() { chatWindow.classList.remove('active'); });

        function sendMessage() {
            var msg = chatInput.value.trim();
            if (!msg) return;
            addMsg(msg, 'user');
            chatInput.value = '';
            showTyping();
            fetch('/api/chatbot/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg }) })
            .then(function(r) { return r.json(); })
            .then(function(d) { removeTyping(); addMsg(d.response, 'bot'); })
            .catch(function() { removeTyping(); addMsg('Sorry, something went wrong! 😅', 'bot'); });
        }
        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });

        function addMsg(text, sender) {
            var d = document.createElement('div'); d.className = 'chat-msg ' + sender;
            var b = document.createElement('div'); b.className = 'chat-bubble';
            b.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/_(.*?)_/g, '<em>$1</em>').replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>').replace(/\n/g, '<br>');
            d.appendChild(b); chatMessages.appendChild(d); scrollChat();
        }
        function showTyping() {
            var d = document.createElement('div'); d.className = 'chat-msg bot'; d.id = 'typingIndicator';
            d.innerHTML = '<div class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>';
            chatMessages.appendChild(d); scrollChat();
        }
        function removeTyping() { var e = document.getElementById('typingIndicator'); if (e) e.remove(); }
        function scrollChat() { chatMessages.scrollTop = chatMessages.scrollHeight; }
    }

    // ===== PREMIUM SMOOTH PAGE TRANSITIONS =====
    var overlay = document.getElementById('pageTransition');
    var mainContent = document.querySelector('.main-content');
    var progressBar = overlay ? overlay.querySelector('.transition-progress') : null;

    // Clear overlay on page load (handles back/forward button)
    if (overlay) {
        overlay.classList.remove('active');
        if (progressBar) progressBar.style.width = '0';
    }

    // Intercept internal link clicks for smooth exit
    document.addEventListener('click', function(e) {
        var link = e.target.closest('a');
        if (!link) return;

        var href = link.getAttribute('href');
        if (!href) return;

        // Skip: hash-only links, external, new tabs, javascript:, # anchors on same page, cart actions
        if (href.startsWith('#') ||
            href.startsWith('javascript') ||
            link.target === '_blank' ||
            link.hasAttribute('download') ||
            link.classList.contains('add-to-cart-btn') ||
            link.classList.contains('remove-item-btn') ||
            link.classList.contains('qty-btn')) {
            return;
        }

        // Skip external links
        try {
            var url = new URL(href, window.location.origin);
            if (url.origin !== window.location.origin) return;
        } catch(ex) { return; }

        // Skip hash links to same page
        if (href.includes('#') && href.split('#')[0] === '' ) return;

        e.preventDefault();

        // Start the glide-out transition
        if (overlay && mainContent) {
            // Phase 1: Slide content out
            mainContent.classList.remove('page-enter');
            mainContent.classList.add('page-exit');

            // Phase 2: After content exits, bring in the curtain
            setTimeout(function() {
                overlay.classList.add('active');

                // Phase 3: Progress bar animation
                if (progressBar) {
                    progressBar.style.width = '70%';
                    setTimeout(function() {
                        progressBar.style.width = '100%';
                    }, 350);
                }

                // Phase 4: Navigate after curtain fully covers
                setTimeout(function() {
                    window.location.href = href;
                }, 500);
            }, 280);
        } else {
            window.location.href = href;
        }
    });

    // Handle form submissions with smooth transitions
    document.querySelectorAll('form').forEach(function(form) {
        // Skip search forms and chatbot forms
        if (form.classList.contains('search-form') || form.closest('.chatbot-window')) return;
        
        form.addEventListener('submit', function() {
            if (overlay && mainContent) {
                mainContent.classList.remove('page-enter');
                mainContent.classList.add('page-exit');
                setTimeout(function() {
                    overlay.classList.add('active');
                    if (progressBar) progressBar.style.width = '90%';
                }, 200);
            }
        });
    });
});

// Handle browser back/forward — clear overlay and reset states
window.addEventListener('pageshow', function(e) {
    var overlay = document.getElementById('pageTransition');
    var progressBar = overlay ? overlay.querySelector('.transition-progress') : null;
    var mainContent = document.querySelector('.main-content');

    if (overlay) {
        overlay.classList.remove('active');
        if (progressBar) progressBar.style.width = '0';
    }

    if (mainContent) {
        mainContent.classList.remove('page-exit');
        mainContent.classList.add('page-enter');
    }
});

// Ensure transitions clean up on full load
window.addEventListener('load', function() {
    var overlay = document.getElementById('pageTransition');
    if (overlay) overlay.classList.remove('active');
});

// ============================================================
//  PRODUCT COMPARISON SYSTEM (localStorage)
// ============================================================

function addToCompare(id, name, image, price) {
    var list = JSON.parse(localStorage.getItem('smartshop_compare') || '[]');

    // Check duplicates
    if (list.some(function(item) { return item.id === id; })) {
        showCompareToast('Product already in comparison list', 'warning');
        return;
    }

    // Max 4
    if (list.length >= 4) {
        showCompareToast('Maximum 4 products can be compared', 'warning');
        return;
    }

    list.push({ id: id, name: name, image: image, price: price });
    localStorage.setItem('smartshop_compare', JSON.stringify(list));
    updateCompareUI();
    showCompareToast('"' + name + '" added for comparison');
}

function removeFromCompare(id) {
    var list = JSON.parse(localStorage.getItem('smartshop_compare') || '[]');
    list = list.filter(function(item) { return item.id !== id; });
    localStorage.setItem('smartshop_compare', JSON.stringify(list));
    updateCompareUI();
    showCompareToast('Product removed from comparison');
}

function clearCompareAll() {
    localStorage.removeItem('smartshop_compare');
    updateCompareUI();
    showCompareToast('Comparison list cleared');
}

function updateCompareUI() {
    var list = JSON.parse(localStorage.getItem('smartshop_compare') || '[]');
    var count = list.length;

    // Navbar badge
    var badge = document.getElementById('compareBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    // Update navbar compare link URL
    var navLink = document.getElementById('navCompareLink');
    if (navLink) {
        var ids = list.map(function(item) { return item.id; });
        navLink.href = '/compare/' + (ids.length > 0 ? '?ids=' + ids.join(',') : '');
    }

    // Floating bar
    var bar = document.getElementById('compareFloatBar');
    var itemsEl = document.getElementById('compareFloatItems');
    var countEl = document.getElementById('compareFloatCount');
    var floatBtn = document.getElementById('compareFloatBtn');

    if (bar) {
        bar.style.display = count > 0 ? 'flex' : 'none';
    }
    if (countEl) {
        countEl.textContent = count + ' product' + (count !== 1 ? 's' : '');
    }
    if (floatBtn) {
        var ids2 = list.map(function(item) { return item.id; });
        floatBtn.href = '/compare/?ids=' + ids2.join(',');
    }

    // Thumbnails
    if (itemsEl) {
        var html = '';
        list.forEach(function(item) {
            html += '<div class="compare-float-thumb">';
            if (item.image) {
                html += '<img src="' + item.image + '" alt="' + item.name + '">';
            } else {
                html += '<i class="fas fa-image"></i>';
            }
            html += '<button class="compare-float-remove" onclick="removeFromCompare(' + item.id + ')"><i class="fas fa-times"></i></button>';
            html += '</div>';
        });
        // Empty slots
        for (var i = count; i < 4; i++) {
            html += '<div class="compare-float-thumb empty"><i class="fas fa-plus"></i></div>';
        }
        itemsEl.innerHTML = html;
    }

    // Update compare buttons to show active state
    document.querySelectorAll('.btn-compare').forEach(function(btn) {
        var onclick = btn.getAttribute('onclick') || '';
        var match = onclick.match(/addToCompare\((\d+)/);
        if (match) {
            var pid = parseInt(match[1]);
            if (list.some(function(item) { return item.id === pid; })) {
                btn.classList.add('compare-active');
                btn.title = 'Already comparing';
            } else {
                btn.classList.remove('compare-active');
                btn.title = 'Compare';
            }
        }
    });
}

function showCompareToast(msg, type) {
    var toast = document.getElementById('compareToast');
    var msgEl = document.getElementById('compareToastMsg');
    if (!toast || !msgEl) return;

    msgEl.textContent = msg;
    toast.className = 'compare-toast';
    if (type === 'warning') toast.classList.add('toast-warning');

    toast.classList.add('toast-show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(function() {
        toast.classList.remove('toast-show');
    }, 2500);
}

// Init compare UI on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCompareUI();

    // Float bar clear button
    var clearBtn = document.getElementById('compareFloatClear');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearCompareAll);
    }
});
