/* =====================================================
   BRANDCODE - Main JavaScript
   Luxury Streetwear Store
   ===================================================== */

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================
    // 1. Mobile Menu Toggle with Animation
    // =========================================================
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const hamburger1 = document.getElementById('hamburger1');
    const hamburger2 = document.getElementById('hamburger2');
    const hamburger3 = document.getElementById('hamburger3');
    let mobileMenuOpen = false;

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function () {
            mobileMenuOpen = !mobileMenuOpen;
            if (mobileMenuOpen) {
                mobileMenu.classList.remove('hidden');
                mobileMenu.classList.add('mobile-menu-enter');
                if (hamburger1) {
                    hamburger1.style.transform = 'rotate(45deg) translateY(6px)';
                    hamburger2.style.opacity = '0';
                    hamburger3.style.transform = 'rotate(-45deg) translateY(-6px)';
                }
            } else {
                mobileMenu.classList.add('hidden');
                mobileMenu.classList.remove('mobile-menu-enter');
                if (hamburger1) {
                    hamburger1.style.transform = '';
                    hamburger2.style.opacity = '1';
                    hamburger3.style.transform = '';
                }
            }
        });
    }

    // =========================================================
    // 2. Search Overlay Toggle
    // =========================================================
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.getElementById('searchOverlay');

    if (searchToggle && searchOverlay) {
        searchToggle.addEventListener('click', function () {
            searchOverlay.classList.toggle('hidden');
            if (!searchOverlay.classList.contains('hidden')) {
                var input = searchOverlay.querySelector('input');
                if (input) input.focus();
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !searchOverlay.classList.contains('hidden')) {
                searchOverlay.classList.add('hidden');
            }
        });
    }

    // =========================================================
    // 3. Navbar Scroll Effect
    // =========================================================
    const navbar = document.getElementById('navbar');

    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 100) {
                navbar.classList.add('shadow-lg');
            } else {
                navbar.classList.remove('shadow-lg');
            }
        }, { passive: true });
    }

    // =========================================================
    // 4. Product Page: Image Gallery
    // =========================================================
    const mainImage = document.getElementById('mainProductImage');
    const thumbnails = document.querySelectorAll('.product-thumbnail');

    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                var newSrc = this.dataset.src || this.querySelector('img').src;
                mainImage.style.opacity = '0';
                mainImage.style.transition = 'opacity 0.3s ease';
                setTimeout(function () {
                    mainImage.src = newSrc;
                    mainImage.style.opacity = '1';
                }, 300);

                thumbnails.forEach(function (t) {
                    t.classList.remove('ring-2', 'ring-[#d4a853]');
                    t.classList.add('ring-1', 'ring-white/10');
                });
                this.classList.remove('ring-1', 'ring-white/10');
                this.classList.add('ring-2', 'ring-[#d4a853]');
            });
        });
    }

    // =========================================================
    // 5. Product Page: Size Selector
    // =========================================================
    const sizeButtons = document.querySelectorAll('.size-btn');
    const selectedSizeInput = document.getElementById('selectedSize');
    const addToCartBtn = document.getElementById('addToCartBtn');

    if (sizeButtons.length > 0) {
        sizeButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (this.disabled || this.dataset.stock === '0') return;

                sizeButtons.forEach(function (b) {
                    b.classList.remove('bg-[#d4a853]', 'text-black', 'border-[#d4a853]');
                    b.classList.add('bg-[#1a1a1a]', 'text-white', 'border-white/10');
                });
                this.classList.remove('bg-[#1a1a1a]', 'text-white', 'border-white/10');
                this.classList.add('bg-[#d4a853]', 'text-black', 'border-[#d4a853]');

                if (selectedSizeInput) {
                    selectedSizeInput.value = this.dataset.size;
                }
                if (addToCartBtn) {
                    addToCartBtn.disabled = false;
                    addToCartBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                }

                // Update max quantity based on selected size stock
                var qtyInput = document.getElementById('quantityInput');
                if (qtyInput && this.dataset.stock) {
                    qtyInput.max = parseInt(this.dataset.stock);
                    if (parseInt(qtyInput.value) > parseInt(this.dataset.stock)) {
                        qtyInput.value = this.dataset.stock;
                    }
                }
            });
        });
    }

    // =========================================================
    // 6. Product Page: Quantity Selector
    // =========================================================
    const qtyMinus = document.getElementById('qtyMinus');
    const qtyPlus = document.getElementById('qtyPlus');
    const qtyInput = document.getElementById('quantityInput');

    if (qtyMinus && qtyPlus && qtyInput) {
        qtyMinus.addEventListener('click', function () {
            var val = parseInt(qtyInput.value) || 1;
            if (val > 1) {
                qtyInput.value = val - 1;
            }
        });

        qtyPlus.addEventListener('click', function () {
            var val = parseInt(qtyInput.value) || 1;
            var max = parseInt(qtyInput.max) || 99;
            if (val < max) {
                qtyInput.value = val + 1;
            }
        });

        qtyInput.addEventListener('change', function () {
            var val = parseInt(this.value) || 1;
            var max = parseInt(this.max) || 99;
            if (val < 1) this.value = 1;
            if (val > max) this.value = max;
        });
    }

    // =========================================================
    // 7. Product Page: Video Modal
    // =========================================================
    const videoBtn = document.getElementById('openVideoModal');
    const videoModal = document.getElementById('videoModal');
    const closeVideoBtn = document.getElementById('closeVideoModal');

    if (videoBtn && videoModal) {
        videoBtn.addEventListener('click', function () {
            videoModal.classList.remove('hidden');
            videoModal.classList.add('flex');
            document.body.style.overflow = 'hidden';
        });
    }

    if (closeVideoBtn && videoModal) {
        closeVideoBtn.addEventListener('click', function () {
            closeVideoModalFn();
        });
        videoModal.addEventListener('click', function (e) {
            if (e.target === videoModal) closeVideoModalFn();
        });
    }

    function closeVideoModalFn() {
        if (!videoModal) return;
        videoModal.classList.add('hidden');
        videoModal.classList.remove('flex');
        document.body.style.overflow = '';
        var iframe = videoModal.querySelector('iframe');
        if (iframe) {
            var src = iframe.src;
            iframe.src = '';
            iframe.src = src;
        }
        var video = videoModal.querySelector('video');
        if (video) video.pause();
    }

    // =========================================================
    // 8. Flash Message Auto-dismiss
    // =========================================================
    var flashToasts = document.querySelectorAll('.toast');
    flashToasts.forEach(function (toast) {
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100px)';
            toast.style.transition = 'all 0.5s ease';
            setTimeout(function () {
                toast.remove();
            }, 500);
        }, 5000);
    });

    // =========================================================
    // 9. Smooth Scroll for Anchor Links
    // =========================================================
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') return;
            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // =========================================================
    // 10. Lazy Loading Images (IntersectionObserver)
    // =========================================================
    var lazyImages = document.querySelectorAll('img[data-src]');
    if (lazyImages.length > 0 && 'IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    img.classList.add('animate-fade-in');
                    imageObserver.unobserve(img);
                }
            });
        }, { rootMargin: '100px' });

        lazyImages.forEach(function (img) {
            imageObserver.observe(img);
        });
    }

    // =========================================================
    // 11. Back to Top Button
    // =========================================================
    var backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'backToTop';
    backToTopBtn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>';
    backToTopBtn.className = 'fixed bottom-6 right-6 z-50 w-12 h-12 bg-[#d4a853] text-black rounded-full flex items-center justify-center shadow-lg hover:bg-[#c8a04a] transition-all duration-300 opacity-0 pointer-events-none';
    backToTopBtn.style.transform = 'translateY(20px)';
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', function () {
        if (window.scrollY > 500) {
            backToTopBtn.style.opacity = '1';
            backToTopBtn.style.pointerEvents = 'auto';
            backToTopBtn.style.transform = 'translateY(0)';
        } else {
            backToTopBtn.style.opacity = '0';
            backToTopBtn.style.pointerEvents = 'none';
            backToTopBtn.style.transform = 'translateY(20px)';
        }
    }, { passive: true });

    backToTopBtn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // =========================================================
    // 12. Product Card Hover Effects (animate on scroll)
    // =========================================================
    var productCards = document.querySelectorAll('.product-card');
    if (productCards.length > 0 && 'IntersectionObserver' in window) {
        var cardObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { rootMargin: '50px', threshold: 0.1 });

        productCards.forEach(function (card, index) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease ' + (index % 4) * 0.1 + 's, transform 0.6s ease ' + (index % 4) * 0.1 + 's';
            cardObserver.observe(card);
        });
    }

    // =========================================================
    // 13. Filter Sidebar Toggle on Mobile
    // =========================================================
    var filterToggle = document.getElementById('filterToggle');
    var filterSidebar = document.getElementById('filterSidebar');
    var filterOverlay = document.getElementById('filterOverlay');

    if (filterToggle && filterSidebar) {
        filterToggle.addEventListener('click', function () {
            filterSidebar.classList.toggle('-translate-x-full');
            filterSidebar.classList.toggle('translate-x-0');
            if (filterOverlay) filterOverlay.classList.toggle('hidden');
        });

        if (filterOverlay) {
            filterOverlay.addEventListener('click', function () {
                filterSidebar.classList.add('-translate-x-full');
                filterSidebar.classList.remove('translate-x-0');
                filterOverlay.classList.add('hidden');
            });
        }
    }

    // =========================================================
    // 14. Search with Debounce
    // =========================================================
    var searchInputs = document.querySelectorAll('input[data-search-debounce]');
    searchInputs.forEach(function (input) {
        var timeout = null;
        input.addEventListener('input', function () {
            var url = this.dataset.searchDebounce;
            var target = this.dataset.searchTarget;
            var self = this;
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                var query = self.value.trim();
                if (query.length < 2) return;
                fetch(url + '?search=' + encodeURIComponent(query), {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(function (r) { return r.text(); })
                .then(function (html) {
                    var container = document.getElementById(target);
                    if (container) container.innerHTML = html;
                })
                .catch(function () { });
            }, 400);
        });
    });

}); // End DOMContentLoaded


// =============================================================
// CART MANAGEMENT
// =============================================================

async function addToCart(productId, size, quantity) {
    if (!size) {
        showToast('\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0440\u0430\u0437\u043C\u0435\u0440', 'warning');
        return;
    }
    quantity = quantity || 1;

    try {
        var response = await fetch('/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: productId,
                size: size,
                quantity: quantity
            })
        });

        var data = await response.json();

        if (data.success) {
            showToast('\u0422\u043E\u0432\u0430\u0440 \u0434\u043E\u0431\u0430\u0432\u043B\u0435\u043D \u0432 \u043A\u043E\u0440\u0437\u0438\u043D\u0443', 'success');
            updateCartBadge(data.cart_count);
        } else {
            showToast(data.message || '\u041E\u0448\u0438\u0431\u043A\u0430 \u043F\u0440\u0438 \u0434\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u0438\u0438', 'error');
        }
    } catch (err) {
        showToast('\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u0435\u0442\u0438. \u041F\u043E\u043F\u0440\u043E\u0431\u0443\u0439\u0442\u0435 \u0435\u0449\u0451 \u0440\u0430\u0437.', 'error');
    }
}

async function updateCartItem(index, quantity) {
    try {
        var response = await fetch('/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                index: index,
                quantity: quantity
            })
        });

        var data = await response.json();

        if (data.success) {
            if (quantity <= 0) {
                removeCartItemFromDOM(index);
            } else {
                var subtotalEl = document.querySelector('[data-subtotal="' + index + '"]');
                if (subtotalEl) {
                    subtotalEl.textContent = formatPrice(data.item_subtotal) + ' \u20B8';
                }
            }
            var totalEl = document.getElementById('cartTotal');
            if (totalEl) totalEl.textContent = formatPrice(data.cart_total) + ' \u20B8';
            updateCartBadge(data.cart_count);

            if (data.cart_count === 0) {
                showEmptyCartState();
            }
        } else {
            showToast(data.message || '\u041E\u0448\u0438\u0431\u043A\u0430 \u043E\u0431\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F', 'error');
        }
    } catch (err) {
        showToast('\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u0435\u0442\u0438', 'error');
    }
}

async function removeCartItem(index) {
    try {
        var response = await fetch('/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index: index })
        });

        var data = await response.json();

        if (data.success) {
            removeCartItemFromDOM(index);
            var totalEl = document.getElementById('cartTotal');
            if (totalEl) totalEl.textContent = formatPrice(data.cart_total) + ' \u20B8';
            updateCartBadge(data.cart_count);
            showToast('\u0422\u043E\u0432\u0430\u0440 \u0443\u0434\u0430\u043B\u0451\u043D \u0438\u0437 \u043A\u043E\u0440\u0437\u0438\u043D\u044B', 'success');

            if (data.cart_count === 0) {
                showEmptyCartState();
            }
        } else {
            showToast(data.message || '\u041E\u0448\u0438\u0431\u043A\u0430 \u0443\u0434\u0430\u043B\u0435\u043D\u0438\u044F', 'error');
        }
    } catch (err) {
        showToast('\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u0435\u0442\u0438', 'error');
    }
}

function removeCartItemFromDOM(index) {
    var row = document.querySelector('[data-cart-item="' + index + '"]');
    if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-30px)';
        row.style.transition = 'all 0.4s ease';
        setTimeout(function () { row.remove(); }, 400);
    }
}

function showEmptyCartState() {
    var container = document.getElementById('cartContainer');
    if (container) {
        container.innerHTML =
            '<div class="text-center py-20">' +
            '<svg class="w-20 h-20 mx-auto text-gray-700 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>' +
            '</svg>' +
            '<h2 class="text-2xl font-bold text-gray-400 mb-2">\u041A\u043E\u0440\u0437\u0438\u043D\u0430 \u043F\u0443\u0441\u0442\u0430</h2>' +
            '<p class="text-gray-600 mb-8">\u0414\u043E\u0431\u0430\u0432\u044C\u0442\u0435 \u0442\u043E\u0432\u0430\u0440\u044B \u0438\u0437 \u043A\u0430\u0442\u0430\u043B\u043E\u0433\u0430</p>' +
            '<a href="/catalog" class="bg-[#d4a853] hover:bg-[#c8a04a] text-black font-semibold px-8 py-3 rounded-lg transition-all">' +
            '\u041F\u0435\u0440\u0435\u0439\u0442\u0438 \u0432 \u043A\u0430\u0442\u0430\u043B\u043E\u0433</a>' +
            '</div>';
    }
}

function updateCartBadge(count) {
    var badge = document.getElementById('cartBadge');
    if (count > 0) {
        if (!badge) {
            var cartLink = document.querySelector('a[href="/cart"]');
            if (cartLink) {
                badge = document.createElement('span');
                badge.id = 'cartBadge';
                badge.className = 'absolute -top-1 -right-1 w-4 h-4 bg-[#d4a853] text-black text-[10px] font-bold rounded-full flex items-center justify-center badge-pulse';
                cartLink.appendChild(badge);
            }
        }
        if (badge) badge.textContent = count;
    } else if (badge) {
        badge.remove();
    }
}


// =============================================================
// WISHLIST TOGGLE
// =============================================================

async function toggleWishlist(productId, button) {
    try {
        var response = await fetch('/wishlist/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });

        var data = await response.json();

        if (data.success) {
            var svg = button.querySelector('svg');
            if (data.in_wishlist) {
                svg.setAttribute('fill', 'currentColor');
                button.classList.add('text-red-500');
                button.classList.remove('text-gray-400');
                showToast('\u0414\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u043E \u0432 \u0438\u0437\u0431\u0440\u0430\u043D\u043D\u043E\u0435', 'success');
            } else {
                svg.setAttribute('fill', 'none');
                button.classList.remove('text-red-500');
                button.classList.add('text-gray-400');
                showToast('\u0423\u0434\u0430\u043B\u0435\u043D\u043E \u0438\u0437 \u0438\u0437\u0431\u0440\u0430\u043D\u043D\u043E\u0433\u043E', 'success');
            }
        }
    } catch (err) {
        showToast('\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u0435\u0442\u0438', 'error');
    }
}


// =============================================================
// CHECKOUT: Build Order Messages
// =============================================================

function buildOrderMessage() {
    var nameEl = document.getElementById('checkoutName');
    var phoneEl = document.getElementById('checkoutPhone');
    var cityEl = document.getElementById('checkoutCity');
    var addressEl = document.getElementById('checkoutAddress');
    var commentEl = document.getElementById('checkoutComment');

    var name = nameEl ? nameEl.value.trim() : '';
    var phone = phoneEl ? phoneEl.value.trim() : '';
    var city = cityEl ? cityEl.value.trim() : '';
    var address = addressEl ? addressEl.value.trim() : '';
    var comment = commentEl ? commentEl.value.trim() : '';

    if (!name || !phone) {
        showToast('\u0417\u0430\u043F\u043E\u043B\u043D\u0438\u0442\u0435 \u0438\u043C\u044F \u0438 \u0442\u0435\u043B\u0435\u0444\u043E\u043D', 'warning');
        return null;
    }

    // Collect cart items from DOM
    var cartItems = document.querySelectorAll('[data-cart-item]');
    var itemsText = '';
    var total = 0;

    cartItems.forEach(function (item) {
        var itemName = item.dataset.itemName || '';
        var itemSize = item.dataset.itemSize || '';
        var itemQty = item.dataset.itemQty || '1';
        var itemPrice = item.dataset.itemPrice || '0';
        var subtotal = parseInt(itemPrice) * parseInt(itemQty);
        total += subtotal;
        itemsText += '\u2022 ' + itemName;
        if (itemSize) itemsText += ' (' + itemSize + ')';
        itemsText += ' x' + itemQty + ' = ' + formatPrice(subtotal) + ' \u20B8\n';
    });

    var message = '\uD83D\uDCE6 \u041D\u043E\u0432\u044B\u0439 \u0437\u0430\u043A\u0430\u0437 \u0438\u0437 BRANDCODE\n\n';
    message += '\uD83D\uDC64 ' + name + '\n';
    message += '\uD83D\uDCDE ' + phone + '\n';
    if (city) message += '\uD83C\uDFD9 ' + city + '\n';
    if (address) message += '\uD83D\uDCCD ' + address + '\n';
    message += '\n\uD83D\uDED2 \u0422\u043E\u0432\u0430\u0440\u044B:\n' + itemsText;
    message += '\n\uD83D\uDCB0 \u0418\u0442\u043E\u0433\u043E: ' + formatPrice(total) + ' \u20B8';
    if (comment) message += '\n\n\uD83D\uDCAC \u041A\u043E\u043C\u043C\u0435\u043D\u0442\u0430\u0440\u0438\u0439: ' + comment;

    return message;
}

function validateCheckoutForm() {
    var nameEl = document.getElementById('checkoutName');
    var phoneEl = document.getElementById('checkoutPhone');
    var valid = true;

    if (nameEl && !nameEl.value.trim()) {
        nameEl.classList.add('border-red-500');
        valid = false;
    } else if (nameEl) {
        nameEl.classList.remove('border-red-500');
    }

    if (phoneEl && !phoneEl.value.trim()) {
        phoneEl.classList.add('border-red-500');
        valid = false;
    } else if (phoneEl) {
        phoneEl.classList.remove('border-red-500');
    }

    if (!valid) {
        showToast('\u0417\u0430\u043F\u043E\u043B\u043D\u0438\u0442\u0435 \u043E\u0431\u044F\u0437\u0430\u0442\u0435\u043B\u044C\u043D\u044B\u0435 \u043F\u043E\u043B\u044F', 'warning');
    }
    return valid;
}

async function saveOrderToServer() {
    var nameEl = document.getElementById('checkoutName');
    var phoneEl = document.getElementById('checkoutPhone');
    var cityEl = document.getElementById('checkoutCity');
    var addressEl = document.getElementById('checkoutAddress');
    var commentEl = document.getElementById('checkoutComment');

    try {
        var response = await fetch('/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: nameEl ? nameEl.value.trim() : '',
                phone: phoneEl ? phoneEl.value.trim() : '',
                city: cityEl ? cityEl.value.trim() : '',
                address: addressEl ? addressEl.value.trim() : '',
                comment: commentEl ? commentEl.value.trim() : ''
            })
        });
        return await response.json();
    } catch (err) {
        return { success: false };
    }
}

async function orderViaWhatsApp() {
    if (!validateCheckoutForm()) return;
    var message = buildOrderMessage();
    if (!message) return;

    var data = await saveOrderToServer();

    var whatsappNumber = document.getElementById('whatsappNumber');
    var number = whatsappNumber ? whatsappNumber.value : '77001234567';
    var url = 'https://wa.me/' + number + '?text=' + encodeURIComponent(message);
    window.open(url, '_blank');

    if (data.success) {
        showToast('\u0417\u0430\u043A\u0430\u0437 \u043E\u0444\u043E\u0440\u043C\u043B\u0435\u043D! \u041F\u0435\u0440\u0435\u043D\u0430\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u043C \u0432 WhatsApp...', 'success');
    }
}

async function orderViaTelegram() {
    if (!validateCheckoutForm()) return;
    var message = buildOrderMessage();
    if (!message) return;

    var data = await saveOrderToServer();

    var telegramUsername = document.getElementById('telegramUsername');
    var username = telegramUsername ? telegramUsername.value : 'brandcode_kz';
    var url = 'https://t.me/' + username + '?text=' + encodeURIComponent(message);
    window.open(url, '_blank');

    if (data.success) {
        showToast('\u0417\u0430\u043A\u0430\u0437 \u043E\u0444\u043E\u0440\u043C\u043B\u0435\u043D! \u041F\u0435\u0440\u0435\u043D\u0430\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u043C \u0432 Telegram...', 'success');
    }
}

async function orderViaInstagram() {
    if (!validateCheckoutForm()) return;

    var data = await saveOrderToServer();

    var instagramAccount = document.getElementById('instagramAccount');
    var account = instagramAccount ? instagramAccount.value : 'brandcode.kz';
    var url = 'https://ig.me/m/' + account;
    window.open(url, '_blank');

    if (data.success) {
        showToast('\u0417\u0430\u043A\u0430\u0437 \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D! \u041F\u0435\u0440\u0435\u043D\u0430\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u043C \u0432 Instagram...', 'success');
    }
}


// =============================================================
// ADMIN: Slug Auto-generation (Russian Transliteration)
// =============================================================

function transliterateSlug(text) {
    var map = {
        '\u0430': 'a', '\u0431': 'b', '\u0432': 'v', '\u0433': 'g', '\u0434': 'd',
        '\u0435': 'e', '\u0451': 'yo', '\u0436': 'zh', '\u0437': 'z', '\u0438': 'i',
        '\u0439': 'y', '\u043A': 'k', '\u043B': 'l', '\u043C': 'm', '\u043D': 'n',
        '\u043E': 'o', '\u043F': 'p', '\u0440': 'r', '\u0441': 's', '\u0442': 't',
        '\u0443': 'u', '\u0444': 'f', '\u0445': 'kh', '\u0446': 'ts', '\u0447': 'ch',
        '\u0448': 'sh', '\u0449': 'shch', '\u044A': '', '\u044B': 'y', '\u044C': '',
        '\u044D': 'e', '\u044E': 'yu', '\u044F': 'ya',
        '\u0410': 'a', '\u0411': 'b', '\u0412': 'v', '\u0413': 'g', '\u0414': 'd',
        '\u0415': 'e', '\u0401': 'yo', '\u0416': 'zh', '\u0417': 'z', '\u0418': 'i',
        '\u0419': 'y', '\u041A': 'k', '\u041B': 'l', '\u041C': 'm', '\u041D': 'n',
        '\u041E': 'o', '\u041F': 'p', '\u0420': 'r', '\u0421': 's', '\u0422': 't',
        '\u0423': 'u', '\u0424': 'f', '\u0425': 'kh', '\u0426': 'ts', '\u0427': 'ch',
        '\u0428': 'sh', '\u0429': 'shch', '\u042A': '', '\u042B': 'y', '\u042C': '',
        '\u042D': 'e', '\u042E': 'yu', '\u042F': 'ya'
    };

    return text
        .split('')
        .map(function (ch) {
            return map[ch] !== undefined ? map[ch] : ch;
        })
        .join('')
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
}


// =============================================================
// ADMIN: Image Upload Preview + Drag-and-Drop
// =============================================================

function previewImages(input) {
    var preview = document.getElementById('imagePreview');
    if (!preview) return;
    preview.innerHTML = '';
    if (input.files && input.files.length > 0) {
        preview.classList.remove('hidden');
        Array.from(input.files).forEach(function (file) {
            var reader = new FileReader();
            reader.onload = function (e) {
                var div = document.createElement('div');
                div.className = 'relative group';
                div.innerHTML = '<div class="aspect-square rounded-lg overflow-hidden border border-white/10">' +
                    '<img src="' + e.target.result + '" class="w-full h-full object-cover">' +
                    '</div>';
                preview.appendChild(div);
            };
            reader.readAsDataURL(file);
        });
    } else {
        preview.classList.add('hidden');
    }
}

function removeExistingImage(btn, filename) {
    var hiddenInput = document.getElementById('removedImages');
    if (!hiddenInput) return;
    var current = hiddenInput.value ? hiddenInput.value.split(',') : [];
    current.push(filename);
    hiddenInput.value = current.join(',');
    var parent = btn.closest('[data-image]');
    if (parent) {
        parent.style.opacity = '0';
        parent.style.transform = 'scale(0.8)';
        parent.style.transition = 'all 0.3s ease';
        setTimeout(function () { parent.remove(); }, 300);
    }
}


// =============================================================
// ADMIN: Dynamic Size Rows (Add/Remove)
// =============================================================

function addSizeRow() {
    var container = document.getElementById('sizesContainer');
    if (!container) return;
    var row = document.createElement('div');
    row.className = 'flex items-center space-x-3 size-row';
    row.style.opacity = '0';
    row.style.transform = 'translateY(10px)';
    row.innerHTML =
        '<input type="text" name="size_name[]" placeholder="\u0420\u0430\u0437\u043C\u0435\u0440 (S, M, L, 42...)" class="flex-1 bg-[#111] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 text-sm">' +
        '<input type="number" name="size_qty[]" value="0" min="0" placeholder="\u041A\u043E\u043B-\u0432\u043E" class="w-28 bg-[#111] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 text-sm">' +
        '<button type="button" onclick="removeSizeRow(this)" class="p-2.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all">' +
        '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>' +
        '</button>';
    container.appendChild(row);

    // Trigger animation
    requestAnimationFrame(function () {
        row.style.transition = 'all 0.3s ease';
        row.style.opacity = '1';
        row.style.transform = 'translateY(0)';
    });

    row.querySelector('input').focus();
}

function removeSizeRow(btn) {
    var row = btn.closest('.size-row');
    if (!row) return;
    row.style.opacity = '0';
    row.style.transform = 'translateX(20px)';
    row.style.transition = 'all 0.3s ease';
    setTimeout(function () { row.remove(); }, 300);
}


// =============================================================
// TOAST NOTIFICATIONS
// =============================================================

function showToast(message, type) {
    type = type || 'info';
    var container = document.getElementById('toastContainer');
    if (!container) return;

    var toast = document.createElement('div');

    var iconSvg = '';
    var borderColor = 'border-l-[#d4a853]';

    if (type === 'success') {
        borderColor = 'border-l-green-500';
        iconSvg = '<svg class="w-5 h-5 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
    } else if (type === 'error') {
        borderColor = 'border-l-red-500';
        iconSvg = '<svg class="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';
    } else if (type === 'warning') {
        borderColor = 'border-l-yellow-500';
        iconSvg = '<svg class="w-5 h-5 text-yellow-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>';
    } else {
        iconSvg = '<svg class="w-5 h-5 text-[#d4a853] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>';
    }

    toast.className = 'toast rounded-lg px-5 py-4 flex items-center space-x-3 shadow-2xl border border-white/5 border-l-4 ' + borderColor;
    toast.style.background = 'rgba(26, 26, 26, 0.95)';
    toast.style.backdropFilter = 'blur(20px)';
    toast.innerHTML = iconSvg +
        '<span class="text-sm text-gray-200">' + escapeHtml(message) + '</span>' +
        '<button onclick="this.parentElement.remove()" class="text-gray-500 hover:text-white ml-auto flex-shrink-0">' +
        '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>' +
        '</button>';

    container.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(function () {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.5s ease';
        setTimeout(function () { toast.remove(); }, 500);
    }, 5000);
}


// =============================================================
// DELETE CONFIRMATION DIALOGS
// =============================================================

function confirmDelete(url, itemName) {
    var modal = document.getElementById('deleteModal');
    if (modal) {
        var nameEl = document.getElementById('deleteItemName');
        var formEl = document.getElementById('deleteForm');
        if (nameEl) nameEl.textContent = itemName;
        if (formEl) formEl.action = url;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        return;
    }

    // Fallback: browser confirm
    if (confirm('\u0423\u0434\u0430\u043B\u0438\u0442\u044C "' + itemName + '"? \u042D\u0442\u043E \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043D\u0435\u043B\u044C\u0437\u044F \u043E\u0442\u043C\u0435\u043D\u0438\u0442\u044C.')) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        document.body.appendChild(form);
        form.submit();
    }
}

function closeDeleteModal() {
    var modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}


// =============================================================
// UTILITY FUNCTIONS
// =============================================================

function formatPrice(num) {
    return Number(num).toLocaleString('ru-RU');
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modals on Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeDeleteModal();
        var videoModal = document.getElementById('videoModal');
        if (videoModal && !videoModal.classList.contains('hidden')) {
            videoModal.classList.add('hidden');
            videoModal.classList.remove('flex');
            document.body.style.overflow = '';
        }
    }
});
