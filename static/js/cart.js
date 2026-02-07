/**
 * Carrinho de compras Telmoz
 * Armazena no localStorage, permite múltiplos produtos e envia para WhatsApp
 */
(function() {
    const CART_KEY = 'telmoz_cart';

    function getCart() {
        try {
            const data = localStorage.getItem(CART_KEY);
            return data ? JSON.parse(data) : {};
        } catch (e) {
            return {};
        }
    }

    function saveCart(cart) {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        updateCartUI();
    }

    function getCartCount() {
        const cart = getCart();
        return Object.values(cart).reduce((sum, item) => sum + item.qty, 0);
    }

    function getCartTotal() {
        const cart = getCart();
        return Object.values(cart).reduce((sum, item) => sum + (item.price * item.qty), 0);
    }

    function addToCart(productId, name, price, maxQty) {
        const cart = getCart();
        const existing = cart[productId];
        const currentQty = existing ? existing.qty : 0;
        const newQty = Math.min(currentQty + 1, maxQty || 999);

        if (newQty > 0) {
            cart[productId] = { name, price, qty: newQty };
            saveCart(cart);
        }
    }

    function updateCartItem(productId, qty) {
        const cart = getCart();
        if (cart[productId]) {
            if (qty <= 0) {
                delete cart[productId];
            } else {
                cart[productId].qty = qty;
            }
            saveCart(cart);
        }
    }

    function removeFromCart(productId) {
        const cart = getCart();
        delete cart[productId];
        saveCart(cart);
    }

    function updateCartUI() {
        const badge = document.getElementById('cartBadge');
        const cartItems = document.getElementById('cartItems');
        const cartFooter = document.getElementById('cartFooter');
        const cartTotal = document.getElementById('cartTotal');
        const cartEmpty = document.getElementById('cartEmpty');

        if (!badge) return;

        const cart = getCart();
        const items = Object.entries(cart);
        const count = getCartCount();

        badge.textContent = count;
        badge.classList.toggle('empty', count === 0);

        if (count === 0) {
            if (cartEmpty) {
                cartEmpty.style.display = 'block';
                cartEmpty.textContent = 'O carrinho está vazio.';
            }
            if (cartItems) {
                const existingItems = cartItems.querySelectorAll('.cart-item');
                existingItems.forEach(el => el.remove());
            }
            if (cartFooter) cartFooter.style.display = 'none';
            return;
        }

        if (cartEmpty) cartEmpty.style.display = 'none';

        if (cartItems) {
            const existingItems = cartItems.querySelectorAll('.cart-item');
            existingItems.forEach(el => el.remove());

            items.forEach(([id, item]) => {
                const div = document.createElement('div');
                div.className = 'cart-item';
                div.dataset.productId = id;
                div.innerHTML = `
                    <div class="cart-item-info">
                        <div class="cart-item-name">${escapeHtml(item.name)}</div>
                        <div class="cart-item-price">MT ${item.price.toFixed(2)} × ${item.qty}</div>
                    </div>
                    <div class="cart-item-qty">
                        <button type="button" data-action="minus">−</button>
                        <span>${item.qty}</span>
                        <button type="button" data-action="plus">+</button>
                    </div>
                    <button type="button" class="cart-remove" data-action="remove" aria-label="Remover">🗑</button>
                `;
                cartItems.appendChild(div);
            });
        }

        if (cartTotal) {
            cartTotal.textContent = 'Total: MT ' + getCartTotal().toFixed(2);
        }
        if (cartFooter) cartFooter.style.display = 'block';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function openCart() {
        document.getElementById('cartDrawer')?.classList.add('open');
        document.getElementById('cartOverlay')?.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeCart() {
        document.getElementById('cartDrawer')?.classList.remove('open');
        document.getElementById('cartOverlay')?.classList.remove('open');
        document.body.style.overflow = '';
    }

    function buildWhatsAppMessage() {
        const cart = getCart();
        const lines = ['Olá! Gostaria de encomendar:'];
        let total = 0;

        Object.entries(cart).forEach(([id, item]) => {
            const subtotal = item.price * item.qty;
            total += subtotal;
            lines.push(`• ${item.name} x${item.qty} - MT ${subtotal.toFixed(2)}`);
        });
        lines.push('');
        lines.push(`*Total: MT ${total.toFixed(2)}*`);

        return lines.join('\n');
    }

    function init() {
        const cartBtn = document.getElementById('cartBtn');
        const cartClose = document.getElementById('cartClose');
        const cartOverlay = document.getElementById('cartOverlay');
        const cartCheckout = document.getElementById('cartCheckout');

        if (cartBtn) {
            cartBtn.addEventListener('click', openCart);
        }
        if (cartClose) {
            cartClose.addEventListener('click', closeCart);
        }
        if (cartOverlay) {
            cartOverlay.addEventListener('click', closeCart);
        }

        if (cartCheckout) {
            cartCheckout.addEventListener('click', function(e) {
                e.preventDefault();
                const count = getCartCount();
                if (count === 0) return;
                const config = window.TELMOZ_CONFIG || {};
                const number = (config.whatsappNumber || '').replace(/\D/g, '');
                const message = encodeURIComponent(buildWhatsAppMessage());
                const url = `https://wa.me/${number}?text=${message}`;
                window.open(url, '_blank');
                closeCart();
            });
        }

        document.addEventListener('click', function(e) {
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const productId = cartItem.dataset.productId;
            const action = e.target.dataset?.action;

            if (action === 'remove') {
                removeFromCart(productId);
            } else if (action === 'minus') {
                const cart = getCart();
                const item = cart[productId];
                if (item) updateCartItem(productId, item.qty - 1);
            } else if (action === 'plus') {
                const cart = getCart();
                const item = cart[productId];
                if (item) updateCartItem(productId, item.qty + 1);
            }
        });

        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn-add-cart');
            if (!btn) return;

            const card = btn.closest('.product-card');
            if (!card) return;

            const id = card.dataset.productId;
            const name = card.dataset.productName;
            const price = parseFloat(card.dataset.productPrice);
            const maxQty = parseInt(card.dataset.productQuantity, 10) || 999;

            if (id && name && !isNaN(price)) {
                addToCart(id, name, price, maxQty);
                openCart();
            }
        });

        updateCartUI();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
