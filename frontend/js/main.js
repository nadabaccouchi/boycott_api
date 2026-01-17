const app = {
    init: () => {
        window.addEventListener('hashchange', app.handleRoute);
        window.addEventListener('auth-change', UI.updateAuthUI);

        // Initial setup
        UI.updateAuthUI();
        app.handleRoute();

        // Load initial data
        app.loadCategories();

        // Forms & Inputs
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') app.performSearch();
            });
            searchInput.addEventListener('input', (e) => {
                if (app.currentMode !== 'barcode') {
                    clearTimeout(app.searchTimer);
                    app.searchTimer = setTimeout(() => app.performSearch(), 300);
                }
            });
        }

        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) searchBtn.addEventListener('click', app.performSearch);

        const catFilter = document.getElementById('category-filter');
        if (catFilter) catFilter.addEventListener('change', app.performSearch);

        const boycottFilter = document.getElementById('boycott-filter');
        if (boycottFilter) boycottFilter.addEventListener('change', app.performSearch);

        document.getElementById('login-form')?.addEventListener('submit', app.handleLogin);
        document.getElementById('register-form')?.addEventListener('submit', app.handleRegister);
        document.getElementById('report-form')?.addEventListener('submit', app.handleSubmitReport);

        // Admin Forms
        document.getElementById('admin-brand-form')?.addEventListener('submit', app.handleBrandSubmit);
        document.getElementById('admin-category-form')?.addEventListener('submit', app.handleCategorySubmit);

        // Modal close listeners
        document.querySelectorAll('.close-modal').forEach(span => {
            span.addEventListener('click', () => {
                document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
            });
        });

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('active');
            }
        });
    },

    handleRoute: () => {
        const hash = window.location.hash || '#home';
        const page = hash.substring(1);

        // Internal page validation
        const validPages = ['home', 'explorer', 'login', 'register', 'reports', 'admin', 'about', 'privacy', 'terms'];
        const targetPage = validPages.includes(page) ? page : 'home';

        UI.showSection(targetPage);

        if (targetPage === 'admin' && !Auth.isAdmin()) {
            window.location.hash = '#login';
            return;
        }

        if (targetPage === 'reports' && Auth.isLoggedIn()) {
            app.loadReports();
        }

        if (targetPage === 'admin' && Auth.isAdmin()) {
            app.refreshStats();
        }

        if (targetPage === 'explorer') {
            app.setSearchMode(app.currentMode); // Ensure correct mode UI
        }
    },

    currentMode: 'brands',
    searchTimer: null,

    setSearchMode(mode) {
        app.currentMode = mode;

        // Update Tabs UI
        ['brands', 'products', 'barcode'].forEach(m => {
            const btn = document.getElementById(`tab-${m}`);
            if (btn) {
                btn.classList.toggle('btn-primary', m === mode);
                btn.classList.toggle('btn-outline', m !== mode);
            }
        });

        const input = document.getElementById('search-input');
        const filters = document.getElementById('filter-container');
        const btn = document.getElementById('search-btn');

        if (!input) return;

        if (mode === 'brands') {
            input.placeholder = "Search ethical brand database...";
            if (filters) filters.style.display = 'flex';
            if (btn) btn.style.display = 'none';
        } else if (mode === 'products') {
            input.placeholder = "Search specific products...";
            if (filters) filters.style.display = 'flex';
            if (btn) btn.style.display = 'none';
        } else if (mode === 'barcode') {
            input.placeholder = "Input 8 or 13 digit barcode...";
            if (filters) filters.style.display = 'none';
            if (btn) btn.style.display = 'block';
        }

        if (input.value) {
            app.performSearch();
        } else if (mode === 'brands') {
            app.performSearch();
        } else {
            document.getElementById('results-grid').innerHTML = '';
            const barcodeResult = document.getElementById('barcode-result');
            if (barcodeResult) barcodeResult.style.display = 'none';
        }
    },

    async performSearch() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;

        const query = searchInput.value;
        const catId = document.getElementById('category-filter')?.value;
        const boycotted = document.getElementById('boycott-filter')?.checked;

        try {
            if (app.currentMode === 'brands') {
                const params = {};
                if (query) params.search = query;
                if (catId) params.category_id = catId;
                if (boycotted) params.boycott_status = 'true';

                const data = await API.getBrands(params);
                UI.renderBrands(data);

            } else if (app.currentMode === 'products') {
                const params = {};
                if (query) params.search = query;
                if (catId) params.category_id = catId;

                const data = await API.getProducts(params);
                let filtered = data;
                if (boycotted) {
                    filtered = data.filter(p => p.brand && p.brand.boycott_status);
                }
                UI.renderProducts(filtered);

            } else if (app.currentMode === 'barcode') {
                if (!query) return;
                if (!/^\d{8,14}$/.test(query)) {
                    alert("Please enter a valid numeric barcode (8-14 digits).");
                    return;
                }
                const data = await API.getBarcode(query);
                UI.renderBarcodeResult(data);
            }
        } catch (error) {
            console.error('Search failed', error);
            if (app.currentMode === 'barcode') {
                UI.renderBarcodeResult(null);
            }
        }
    },

    async loadCategories() {
        try {
            const cats = await API.getCategories();
            UI.renderCategories(cats);
        } catch (error) {
            console.error('Failed to load categories');
        }
    },

    handleLogin: async (e) => {
        e.preventDefault();
        const email = e.target.email.value;
        const password = e.target.password.value;
        const msgEl = document.getElementById('login-message');

        try {
            await Auth.login(email, password);
            window.location.hash = '#home';
            e.target.reset();
        } catch (error) {
            if (msgEl) {
                msgEl.textContent = error.message;
                msgEl.className = 'message error';
            }
        }
    },

    async loadReports() {
        try {
            const reports = Auth.isAdmin() ? await API.getReports() : await API.getMyReports();
            UI.renderReports(reports);
        } catch (error) {
            console.error('Failed to load reports', error);
            const list = document.getElementById('reports-list');
            if (list) list.innerHTML = '<p>Error syncronizing with server.</p>';
        }
    },

    async handleSubmitReport(e) {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(e.target));
        if (!data.barcode) delete data.barcode;
        if (!data.product_id) delete data.product_id;

        const msgEl = document.getElementById('report-message');

        try {
            await API.createReport(data);
            if (msgEl) {
                msgEl.textContent = 'Thank you! Your report has been submitted for verification.';
                msgEl.className = 'message success';
            }
            e.target.reset();
            if (window.location.hash === '#reports') app.loadReports();
        } catch (error) {
            if (msgEl) {
                msgEl.textContent = error.message;
                msgEl.className = 'message error';
            }
        }
    },

    async updateReport(id, status) {
        if (!confirm(`Confirm moderation action: ${status}?`)) return;
        try {
            await API.updateReport(id, { status });
            app.loadReports();
        } catch (error) {
            alert(error.message);
        }
    },

    handleRegister: async (e) => {
        e.preventDefault();
        const username = e.target.username.value;
        const email = e.target.email.value;
        const password = e.target.password.value;
        const msgEl = document.getElementById('register-message');

        try {
            await API.register(username, email, password);
            if (msgEl) {
                msgEl.textContent = 'Account created! Redirecting to login...';
                msgEl.className = 'message success';
            }
            setTimeout(() => window.location.hash = '#login', 1500);
        } catch (error) {
            if (msgEl) {
                msgEl.textContent = error.message;
                msgEl.className = 'message error';
            }
        }
    },

    async refreshStats() {
        if (!Auth.isAdmin()) return;
        try {
            const stats = await API.getStats();
            UI.renderStats(stats);
        } catch (error) {
            console.error('Failed to load stats', error);
        }
    },

    openBrandModal(brand = null) {
        if (!Auth.isAdmin()) return;

        const modal = document.getElementById('brand-modal');
        const form = document.getElementById('admin-brand-form');
        const msg = document.getElementById('brand-message');
        const title = modal?.querySelector('h2');

        if (!modal || !form) return;

        form.reset();
        if (msg) {
            msg.textContent = '';
            msg.className = 'message';
        }

        if (brand) {
            if (title) title.textContent = 'Edit Brand Details';
            document.getElementById('brand-id').value = brand.id;
            document.getElementById('brand-name').value = brand.name;
            document.getElementById('brand-status').value = brand.boycott_status.toString();
            document.getElementById('brand-logo').value = brand.logo_url || '';
            document.getElementById('brand-reason').value = brand.reason || '';
        } else {
            if (title) title.textContent = 'Add New Brand';
            const idField = document.getElementById('brand-id');
            if (idField) idField.value = '';
        }

        modal.classList.add('active');
    },

    async handleBrandSubmit(e) {
        e.preventDefault();
        const msgEl = document.getElementById('brand-message');
        const form = e.target;
        const id = document.getElementById('brand-id').value;
        const isEdit = !!id;

        const data = {
            name: form.name.value,
            boycott_status: form.boycott_status.value === 'true',
            logo_url: form.logo_url.value || null,
            reason: form.reason.value || null
        };

        try {
            if (isEdit) {
                await API.updateBrand(id, data);
            } else {
                await API.createBrand(data);
            }

            if (msgEl) {
                msgEl.textContent = `Success: Database entry has been ${isEdit ? 'updated' : 'created'}.`;
                msgEl.className = 'message success';
            }

            if (app.currentMode === 'brands') app.performSearch();

            setTimeout(() => {
                document.getElementById('brand-modal')?.classList.remove('active');
            }, 1000);

        } catch (error) {
            if (msgEl) {
                msgEl.textContent = error.message;
                msgEl.className = 'message error';
            }
        }
    },

    async deleteBrand(id) {
        if (!confirm('Permanent Action: Are you sure you want to delete this brand?')) return;
        try {
            await API.deleteBrand(id);
            app.performSearch();
        } catch (err) {
            alert(err.message);
        }
    },

    async editBrand(id) {
        try {
            const brand = await API.getBrand(id);
            app.openBrandModal(brand);
        } catch (error) {
            alert('Cloud Sync Error: ' + error.message);
        }
    },

    openCategoryModal() {
        if (!Auth.isAdmin()) return;
        const modal = document.getElementById('category-modal');
        const msg = document.getElementById('category-message');
        if (msg) msg.textContent = '';
        app.loadCategoriesManage();
        modal?.classList.add('active');
    },

    async loadCategoriesManage() {
        try {
            const cats = await API.getCategories();
            UI.renderCategoriesManage(cats);
        } catch (error) {
            console.error(error);
        }
    },

    async handleCategorySubmit(e) {
        e.preventDefault();
        const msgEl = document.getElementById('category-message');
        const name = e.target.name.value;
        try {
            await API.request('/categories', {
                method: 'POST',
                body: JSON.stringify({ name, slug: name.toLowerCase().replace(/\s+/g, '-') })
            });
            if (msgEl) {
                msgEl.textContent = 'New category added to global database.';
                msgEl.className = 'message success';
            }
            e.target.reset();
            app.loadCategories();
            app.loadCategoriesManage();
        } catch (error) {
            if (msgEl) {
                msgEl.textContent = error.message;
                msgEl.className = 'message error';
            }
        }
    }
};

document.addEventListener('DOMContentLoaded', app.init);
