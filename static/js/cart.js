// Shopping Cart Functionality
class ShoppingCart {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('tajCart') || '[]');
        this.init();
    }

    init() {
        console.log('Shopping cart initialized');
        this.bindEvents();
        this.updateCartDisplay();
        this.showCartWidget();
        this.createCartWidget();
    }

    bindEvents() {
        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart-btn')) {
                this.handleAddToCart(e.target.closest('.add-to-cart-btn'));
            }
        });

        // Cart toggle
        const cartToggle = document.getElementById('cart-toggle');
        if (cartToggle) {
            cartToggle.addEventListener('click', () => this.toggleCart());
        }

        // Clear cart
        const clearCartBtn = document.getElementById('clear-cart');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', () => this.clearCart());
        }

        // Modal events
        this.bindModalEvents();

        // Close cart when clicking outside
        document.addEventListener('click', (e) => {
            const cartWidget = document.getElementById('cart-widget');
            const cartDropdown = document.getElementById('cart-dropdown');
            if (cartWidget && cartDropdown && !cartWidget.contains(e.target)) {
                if (cartDropdown.classList.contains('active')) {
                    cartDropdown.classList.remove('active');
                    console.log('Cart dropdown closed by outside click');
                }
            }
        });
    }

    bindModalEvents() {
        // Spice modal events
        const spiceModal = document.getElementById('spice-modal');
        const drinkModal = document.getElementById('drink-modal');

        // Close modal events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close')) {
                this.closeAllModals();
            }
            if (e.target.classList.contains('modal')) {
                this.closeAllModals();
            }
        });

        // Spice selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('spice-option')) {
                // Check if we're in the drink modal or spice modal
                const drinkModal = e.target.closest('#drink-modal');
                const spiceModal = e.target.closest('#spice-modal');
                
                if (drinkModal) {
                    this.handleSpiceSelectionInDrinkModal(e.target);
                } else if (spiceModal) {
                    this.handleSpiceSelection(e.target);
                }
            }
        });

        // Drink selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('drink-option')) {
                this.handleDrinkSelection(e.target);
            }
        });

        // Portion selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('portion-option')) {
                this.handlePortionSelection(e.target);
            }
        });

        // Price selection (for items with 2p/4p prices)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('price-option') || e.target.closest('.price-option')) {
                const priceOption = e.target.classList.contains('price-option') ? e.target : e.target.closest('.price-option');
                this.handlePriceSelection(priceOption);
            }
        });

        // Curry selection (for set menus)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('curry-option') || e.target.closest('.curry-option')) {
                const curryOption = e.target.classList.contains('curry-option') ? e.target : e.target.closest('.curry-option');
                this.handleCurrySelection(curryOption);
            }
        });

        // Remove cart item
        document.addEventListener('click', (e) => {
            if (e.target.closest('.cart-item-remove')) {
                const index = parseInt(e.target.closest('.cart-item-remove').dataset.index);
                this.removeFromCart(index);
            }
        });

        // Checkout
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => this.checkout());
        }
    }

    handleAddToCart(button) {
        const itemData = {
            id: button.dataset.itemId,
            name: button.dataset.itemName,
            price: parseInt(button.dataset.itemPrice),
            category: button.dataset.itemCategory,
            type: button.dataset.itemType,
            hasPortions: button.dataset.hasPortions === 'true',
            price2p: button.dataset.price2p ? parseInt(button.dataset.price2p) : null,
            price4p: button.dataset.price4p ? parseInt(button.dataset.price4p) : null
        };

        console.log('Adding to cart:', itemData);

        // Store current item data for modal use
        this.currentItem = itemData;

        // Check if item has multiple piece prices (items 4, 5, 6 specifically or any with both prices)
        if (itemData.price2p && itemData.price4p) {
            this.showPriceModal(itemData);
        }
        // Check if it's a set menu item that needs curry selection
        else if (itemData.type === 'set_menu') {
            const excludedIds = ['2', '4', '5', '6', '7', '8', '9', '17', '18'];
            if (!excludedIds.includes(itemData.id)) {
                this.showCurryModal(itemData);
            } else {
                this.showDrinkModal(itemData);
            }
        }
        // Check if it's a curry item (category 7 or 17)
        else if (itemData.category === '7' || itemData.category === '17') {
            this.showSpiceModal(itemData);
        }
        else {
            // Add directly to cart for other items
            this.addToCart(itemData);
        }
    }

    showSpiceModal(itemData) {
        const modal = document.getElementById('spice-modal');
        const itemNameEl = modal.querySelector('.modal-item-name');
        const portionSection = modal.querySelector('.portion-selection');

        itemNameEl.textContent = itemData.name;

        // Show/hide portion selection based on item
        if (itemData.hasPortions) {
            portionSection.style.display = 'block';
        } else {
            portionSection.style.display = 'none';
        }

        // Clear previous selections
        modal.querySelectorAll('.spice-option, .portion-option').forEach(btn => {
            btn.classList.remove('selected');
        });

        modal.classList.add('show');
    }

    showDrinkModal(itemData) {
        const modal = document.getElementById('drink-modal');
        const itemNameEl = modal.querySelector('.modal-item-name');
        const spiceSection = modal.querySelector('.spice-options-for-set');
        const drinkOptions = modal.querySelectorAll('.drink-option');

        itemNameEl.textContent = itemData.name;

        // Clear previous selections
        modal.querySelectorAll('.drink-option, .spice-option').forEach(btn => {
            btn.classList.remove('selected');
        });

        // Check if this is Kid's Lunch (ID 17)
        if (itemData.id === '17') {
            // Hide spice level section for Kid's Lunch
            spiceSection.style.display = 'none';
            
            // Show only Orange and Apple juice options
            drinkOptions.forEach(option => {
                const drinkType = option.dataset.drink;
                if (drinkType === 'orange_juice' || drinkType === 'apple_juice') {
                    option.style.display = 'block';
                } else {
                    option.style.display = 'none';
                }
            });
        } else {
            // Show spice level section for other set menus
            spiceSection.style.display = 'block';
            
            // Show all drink options except juice options
            drinkOptions.forEach(option => {
                const drinkType = option.dataset.drink;
                if (drinkType === 'orange_juice' || drinkType === 'apple_juice') {
                    option.style.display = 'none';
                } else {
                    option.style.display = 'block';
                }
            });
        }

        modal.classList.add('show');
    }

    showPriceModal(itemData) {
        const modal = document.getElementById('price-modal');
        const itemNameEl = modal.querySelector('.modal-item-name');
        const priceOptions = modal.querySelectorAll('.price-option');

        itemNameEl.textContent = itemData.name;

        // Update price displays for pieces
        priceOptions.forEach(option => {
            const portion = option.dataset.portion;
            const priceEl = option.querySelector('.price-option-price');
            const labelEl = option.querySelector('.price-option-label');
            
            if (portion === '2p') {
                priceEl.textContent = `¥${itemData.price2p}`;
                labelEl.textContent = '2 Pieces (2個)';
            } else if (portion === '4p') {
                priceEl.textContent = `¥${itemData.price4p}`;
                labelEl.textContent = '4 Pieces (4個)';
            }
        });

        // Clear previous selections
        priceOptions.forEach(btn => btn.classList.remove('selected'));

        modal.classList.add('show');
    }

    async showCurryModal(itemData) {
        const modal = document.getElementById('curry-modal');
        const itemNameEl = modal.querySelector('.modal-item-name');
        const curryList = document.getElementById('curry-options-list');

        itemNameEl.textContent = itemData.name;

        // Fetch curry items from categories 7 and 17
        try {
            const response = await fetch('/api/menu-items?categories=7,17');
            const data = await response.json();

            // Clear previous options
            curryList.innerHTML = '';

            // Check if we got a valid array
            if (Array.isArray(data) && data.length > 0) {
                // Add curry options
                data.forEach(curry => {
                    const button = document.createElement('button');
                    button.className = 'curry-option';
                    button.dataset.curryId = curry.id;
                    button.dataset.curryName = curry.name;
                    button.textContent = curry.name;
                    curryList.appendChild(button);
                });
            } else {
                curryList.innerHTML = '<p>No curry options available.</p>';
            }
        } catch (error) {
            console.error('Error loading curry options:', error);
            curryList.innerHTML = '<p>Error loading curry options. Please try again.</p>';
        }

        modal.classList.add('show');
    }

    handlePriceSelection(button) {
        // Remove selection from siblings
        button.parentElement.querySelectorAll('.price-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        button.classList.add('selected');

        const portion = button.dataset.portion;
        const itemData = { ...this.currentItem };
        
        // Set the selected price and piece count
        itemData.portion = portion;
        itemData.pieces = portion === '2p' ? 2 : 4;
        itemData.price = portion === '2p' ? itemData.price2p : itemData.price4p;

        // Continue to next step based on item type
        this.closeAllModals();
        
        if (itemData.type === 'set_menu') {
            const excludedIds = ['2', '4', '5', '6', '7', '8', '9', '17', '18'];
            if (!excludedIds.includes(itemData.id)) {
                this.currentItem = itemData; // Update current item with price selection
                this.showCurryModal(itemData);
            } else {
                this.currentItem = itemData; // Update current item with price selection
                this.showDrinkModal(itemData);
            }
        } else if (itemData.category === '7' || itemData.category === '17') {
            this.currentItem = itemData; // Update current item with price selection
            this.showSpiceModal(itemData);
        } else {
            this.addToCart(itemData);
        }
    }

    handleCurrySelection(button) {
        // Remove selection from siblings
        button.parentElement.querySelectorAll('.curry-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        button.classList.add('selected');

        const itemData = { ...this.currentItem };
        itemData.selectedCurry = button.dataset.curryName;
        itemData.selectedCurryId = button.dataset.curryId;

        // Update current item and proceed to drink modal
        this.currentItem = itemData;
        this.closeAllModals();
        this.showDrinkModal(itemData);
    }

    handleSpiceSelection(button) {
        // Remove selection from siblings
        button.parentElement.querySelectorAll('.spice-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        button.classList.add('selected');

        // Check if we can proceed to add to cart
        this.checkSpiceModalCompletion();
    }

    handleDrinkSelection(button) {
        // Remove selection from siblings
        button.parentElement.querySelectorAll('.drink-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        button.classList.add('selected');

        console.log('Drink selected:', button.textContent.trim());

        // Check if we can proceed to add to cart
        this.checkDrinkModalCompletion();
    }

    handleSpiceSelectionInDrinkModal(button) {
        // Remove selection from siblings in the spice-options-for-set container
        const spiceContainer = button.closest('.spice-options-for-set');
        spiceContainer.querySelectorAll('.spice-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        button.classList.add('selected');

        console.log('Spice selected in drink modal:', button.textContent.trim());

        // Check if we can proceed to add to cart
        this.checkDrinkModalCompletion();
    }

    handlePortionSelection(button) {
        // Remove selection from siblings
        button.parentElement.querySelectorAll('.portion-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        button.classList.add('selected');

        // Check if we can proceed to add to cart
        this.checkSpiceModalCompletion();
    }

    checkSpiceModalCompletion() {
        const modal = document.getElementById('spice-modal');
        const selectedSpice = modal.querySelector('.spice-option.selected');
        const portionSection = modal.querySelector('.portion-selection');
        const selectedPortion = modal.querySelector('.portion-option.selected');

        // Check if spice is selected and portion is selected (if required)
        if (selectedSpice && (portionSection.style.display === 'none' || selectedPortion)) {
            // Add to cart with selections
            const itemData = { ...this.currentItem };
            itemData.spiceLevel = selectedSpice.dataset.spice;
            itemData.spiceLevelText = selectedSpice.textContent;

            if (selectedPortion) {
                itemData.portion = selectedPortion.dataset.portion;
                itemData.price = itemData.portion === '2p' ? itemData.price2p : itemData.price4p;
            }

            this.addToCart(itemData);
            this.closeAllModals();
        }
    }

    checkDrinkModalCompletion() {
        const modal = document.getElementById('drink-modal');
        const selectedDrink = modal.querySelector('.drink-option.selected');
        const selectedSpice = modal.querySelector('.spice-options-for-set .spice-option.selected');
        const spiceSection = modal.querySelector('.spice-options-for-set');

        console.log('Checking drink modal completion:');
        console.log('Selected drink:', selectedDrink);
        console.log('Selected spice:', selectedSpice);
        console.log('Spice section visible:', spiceSection.style.display !== 'none');
        console.log('Current item ID:', this.currentItem.id);

        // Check if it's Kid's Lunch (ID 17) - only drink selection required
        if (this.currentItem.id === '17') {
            if (selectedDrink) {
                // Add to cart with only drink selection (no spice level)
                const itemData = { ...this.currentItem };
                itemData.drink = selectedDrink.dataset.drink;
                itemData.drinkText = selectedDrink.textContent.trim();

                console.log('Adding Kid\'s Lunch to cart:', itemData);
                this.addToCart(itemData);
                this.closeAllModals();
            } else {
                console.log('Missing drink selection for Kid\'s Lunch');
            }
        } else {
            // For other set menus, check if both drink and spice are selected
            if (selectedDrink && selectedSpice) {
                // Add to cart with selections
                const itemData = { ...this.currentItem };
                itemData.drink = selectedDrink.dataset.drink;
                itemData.drinkText = selectedDrink.textContent.trim();
                itemData.spiceLevel = selectedSpice.dataset.spice;
                itemData.spiceLevelText = selectedSpice.textContent.trim();

                console.log('Adding set menu to cart:', itemData);
                this.addToCart(itemData);
                this.closeAllModals();
            } else {
                console.log('Missing selections - drink:', !!selectedDrink, 'spice:', !!selectedSpice);
            }
        }
    }

    addToCart(itemData) {
        // Generate unique ID for cart item
        const cartItem = {
            ...itemData,
            cartId: Date.now() + Math.random(),
            quantity: 1,
            timestamp: new Date().toISOString()
        };

        this.cart.push(cartItem);
        this.saveCart();
        this.updateCartDisplay();
        this.showAddedToCartFeedback();
    }

    removeFromCart(index) {
        this.cart.splice(index, 1);
        this.saveCart();
        this.updateCartDisplay();
    }

    clearCart() {
        this.cart = [];
        this.saveCart();
        this.updateCartDisplay();
    }

    toggleCart() {
        const dropdown = document.getElementById('cart-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('active');
        } else {
            console.error('Cart dropdown not found');
        }
    }

    createCartWidget() {
        // Check if cart widget already exists
        if (document.getElementById('cart-widget')) {
            console.log('Cart widget already exists');
            return;
        }

        // Only create cart widget on menu pages
        if (!document.querySelector('.detailed-menu')) {
            console.log('Not a menu page, skipping cart widget creation');
            return;
        }

        console.log('Creating cart widget');
        
        // Get current language
        const isJapanese = this.getCurrentLanguage() === 'jp';
        
        const cartWidget = document.createElement('div');
        cartWidget.id = 'cart-widget';
        cartWidget.className = 'cart-widget';
        cartWidget.innerHTML = `
            <button id="cart-toggle" class="cart-toggle">
                <i class="fas fa-shopping-cart"></i>
                <span id="cart-count" class="cart-count">0</span>
            </button>
            <div id="cart-dropdown" class="cart-dropdown">
                <div class="cart-header">
                    <h3>${isJapanese ? 'カート' : 'Cart'}</h3>
                    <button id="clear-cart" class="clear-cart-btn">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div id="cart-items" class="cart-items">
                    <!-- Cart items will be populated here -->
                </div>
                <div class="cart-footer">
                    <div class="cart-total">
                        <strong>${isJapanese ? '合計' : 'Total'}: ¥<span id="cart-total">0</span></strong>
                    </div>
                    <button id="checkout-btn" class="checkout-btn">
                        ${isJapanese ? '注文を生成' : 'Generate Order'}
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(cartWidget);

        // Re-bind events for the new cart widget
        this.bindCartEvents();
    }

    bindCartEvents() {
        const cartToggle = document.getElementById('cart-toggle');
        const clearCartBtn = document.getElementById('clear-cart');
        
        if (cartToggle) {
            cartToggle.addEventListener('click', () => this.toggleCart());
        }
        
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', () => this.clearCart());
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    }

    updateCartDisplay() {
        const countEl = document.getElementById('cart-count');
        const itemsEl = document.getElementById('cart-items');
        const totalEl = document.getElementById('cart-total');
        const checkoutBtn = document.getElementById('checkout-btn');

        if (!countEl || !itemsEl || !totalEl) return;

        // Get current language
        const isJapanese = this.getCurrentLanguage() === 'jp';

        // Update count
        countEl.textContent = this.cart.length;
        countEl.style.display = this.cart.length > 0 ? 'flex' : 'none';

        // Update items
        if (this.cart.length === 0) {
            itemsEl.innerHTML = `<div style="padding: 2rem; text-align: center; color: hsl(var(--luxury-black));">${isJapanese ? 'カートは空です' : 'Your cart is empty'}</div>`;
            checkoutBtn.disabled = true;
        } else {
            itemsEl.innerHTML = this.cart.map((item, index) => `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <div class="cart-item-name">${item.name}</div>
                        <div class="cart-item-details">
                            ${item.spiceLevelText ? `${isJapanese ? '辛さ' : 'Spice'}: ${item.spiceLevelText}` : ''}
                            ${item.drinkText ? ` | ${isJapanese ? 'ドリンク' : 'Drink'}: ${item.drinkText}` : ''}
                            ${item.portion ? ` | ${item.portion.toUpperCase()}` : ''}
                        </div>
                    </div>
                    <div class="cart-item-price">¥${item.price.toLocaleString()}</div>
                    <button class="cart-item-remove" data-index="${index}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('');
            checkoutBtn.disabled = false;
        }

        // Update total
        const total = this.cart.reduce((sum, item) => sum + item.price, 0);
        totalEl.textContent = total.toLocaleString();
    }

    showCartWidget() {
        const widget = document.getElementById('cart-widget');
        if (widget) {
            widget.style.display = 'block';
        }
    }

    showAddedToCartFeedback() {
        // Simple feedback - could be enhanced with toast notifications
        const cartToggle = document.getElementById('cart-toggle');
        if (cartToggle) {
            cartToggle.style.transform = 'scale(1.2)';
            setTimeout(() => {
                cartToggle.style.transform = 'scale(1)';
            }, 200);
        }
    }

    saveCart() {
        localStorage.setItem('tajCart', JSON.stringify(this.cart));
    }

    async checkout() {
        if (this.cart.length === 0) return;

        const checkoutBtn = document.getElementById('checkout-btn');
        const isJapanese = this.getCurrentLanguage() === 'jp';
        const originalText = checkoutBtn ? checkoutBtn.innerHTML : (isJapanese ? '注文を生成' : 'Generate Order');

        try {
            // Show loading state
            if (checkoutBtn) {
                checkoutBtn.disabled = true;
                checkoutBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${isJapanese ? '処理中...' : 'Processing...'}`;
            }

            // Prepare order data
            const total = this.cart.reduce((sum, item) => sum + item.price, 0);
            const orderData = {
                items: this.cart,
                total_amount: total,
                restaurant_location: this.getCurrentRestaurantLocation(),
                customer_info: {}
            };

            // Send order to backend
            const response = await fetch('/api/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();

            if (result.success) {
                // Show QR code modal
                this.showOrderQRModal(result.order_number, result.qr_code_url, total);
                
                // Clear cart after successful order
                this.clearCart();
                this.toggleCart();
            } else {
                throw new Error(result.error || 'Failed to create order');
            }

        } catch (error) {
            console.error('Checkout error:', error);
            const errorMessage = isJapanese ? 
                '申し訳ございませんが、注文の処理中にエラーが発生しました。再度お試しいただくか、レストランに直接お問い合わせください。' : 
                'Sorry, there was an error processing your order. Please try again or contact the restaurant directly.';
            alert(errorMessage);
        } finally {
            // Restore button state
            if (checkoutBtn) {
                checkoutBtn.disabled = false;
                checkoutBtn.innerHTML = originalText;
            }
        }
    }

    getCurrentRestaurantLocation() {
        // Extract restaurant location from URL path
        const path = window.location.pathname;
        const match = path.match(/\/taj-([^\/]+)/);
        return match ? match[1] : 'unknown';
    }

    showOrderQRModal(orderNumber, qrCodeUrl, total) {
        // Get current language from URL or localStorage
        const currentLang = this.getCurrentLanguage();
        
        // Create and show QR code modal
        const modal = document.createElement('div');
        modal.className = 'modal qr-modal';
        
        const isJapanese = currentLang === 'jp';
        
        modal.innerHTML = `
            <div class="modal-content qr-modal-content">
                <div class="modal-body qr-modal-body">
                    <div class="order-success">
                        <i class="fas fa-check-circle success-icon"></i>
                        <h4>${isJapanese ? '注文が生成されました！' : 'Order Generated!'}</h4>
                        
                        <div class="qr-code-section">
                            <h4>${isJapanese ? 'スタッフにこのQRコードを提示してください：' : 'Show this QR code to staff:'}</h4>
                            <div class="qr-code-container">
                                <img src="${qrCodeUrl}" alt="${isJapanese ? '注文QRコード' : 'Order QR Code'}" class="qr-code-image">
                            </div>
                            <p class="qr-instructions">
                                ${isJapanese ? 
                                    'このQRコードをスタッフに提示して注文してください。<br>このページのスクリーンショットを撮ってスタッフに提示してください。' : 
                                    'Present this QR code to the staff to order.<br>Screenshot this page or keep it open to show the staff to order.'
                                }
                            </p>
                        </div>
                        <p class="order-total">${isJapanese ? '合計' : 'Total'}: ¥${total.toLocaleString()}</p>
                        <h4>${isJapanese ? '注文番号' : 'Order'} #${orderNumber}</h4>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.classList.add('show');

        // Handle modal close - click outside modal to close
        modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('qr-modal')) {
                document.body.removeChild(modal);
            }
        });
    }
    
    getCurrentLanguage() {
        // Check if Japanese language toggle is active
        const japaneseToggle = document.querySelector('.language-label.japanese.active');
        const englishToggle = document.querySelector('.language-label.english.active');
        
        if (japaneseToggle) {
            return 'jp';
        }
        
        if (englishToggle) {
            return 'en';
        }
        
        // Check URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const langParam = urlParams.get('lang');
        if (langParam) {
            return langParam;
        }
        
        // Check localStorage
        const storedLang = localStorage.getItem('tajLanguage');
        if (storedLang) {
            return storedLang;
        }
        
        // Check if we're on a Japanese page
        const path = window.location.pathname;
        if (path.includes('/jp/') || path.includes('_jp')) {
            return 'jp';
        }
        
        // Default to English
        return 'en';
    }
}

// Initialize cart when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, checking for cart initialization');
    // Only initialize cart if we're on a page with menu items or detailed menu
    if (document.querySelector('.add-to-cart-btn') || document.getElementById('cart-widget') || document.querySelector('.detailed-menu')) {
        console.log('Cart-enabled page detected, initializing shopping cart');
        window.tajCart = new ShoppingCart();
    } else {
        console.log('No cart functionality needed on this page');
    }
});

// Listen for language changes and refresh cart
document.addEventListener('click', function(e) {
    if (e.target.closest('.toggle-switch') || e.target.closest('.language-label')) {
        // Language toggle was clicked, refresh cart after a short delay
        setTimeout(() => {
            if (window.tajCart) {
                window.tajCart.updateCartDisplay();
            }
        }, 100);
    }
});
