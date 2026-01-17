class UI {
    static showSection(id) {
        document.querySelectorAll('section').forEach(sec => {
            sec.classList.remove('active');
            sec.style.display = 'none';
        });

        const target = document.getElementById(id);
        if (target) {
            target.style.display = 'block';
            // Trigger reflow for animation
            target.offsetHeight;
            target.classList.add('active');

            // Highlight nav
            document.querySelectorAll('.nav a').forEach(link => {
                link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
            });
        }
    }

    static renderBrandCard(brand) {
        const isBoycotted = brand.boycott_status;
        const badgeClass = isBoycotted ? 'badge-danger' : 'badge-success';
        const badgeText = isBoycotted ? 'Boycott' : 'Safe';
        const icon = isBoycotted ? '⚠️' : '✅';

        return `
            <div class="card brand-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <h3>${brand.name}</h3>
                    <span class="badge ${badgeClass}">${icon} ${badgeText}</span>
                </div>
                <div class="card-body" style="flex: 1;">
                    ${brand.logo_url ? `<img src="${brand.logo_url}" alt="${brand.name}" style="max-height: 40px; margin-bottom: 1rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">` : ''}
                    <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.5;">
                        ${brand.reason || 'Join our movement to help verify this brand’s ethical practices.'}
                    </p>
                </div>
                <div class="badges">
                    ${brand.category ? `<span class="badge" style="background:rgba(99,102,241,0.1); color:var(--primary)">${brand.category}</span>` : ''}
                </div>
                ${Auth.isAdmin() ? `
                <div class="card-footer" style="margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem; display: flex; justify-content: flex-end; gap: 0.5rem;">
                    <button class="btn btn-outline" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" onclick="app.editBrand(${brand.id})">Edit</button>
                    <button class="btn btn-danger" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" onclick="app.deleteBrand(${brand.id})">Delete</button>
                </div>
                ` : ''}
            </div>
        `;
    }

    static renderProductCard(product) {
        const brand = product.brand;
        const isBoycotted = (brand && brand.boycott_status) || false;
        const badgeClass = isBoycotted ? 'badge-danger' : 'badge-success';
        const badgeText = isBoycotted ? 'Conflict Brand' : 'Verified Safe';

        return `
            <div class="card product-card">
                <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 1.5rem;">
                    <div style="width: 48px; height: 48px; background: rgba(0,0,0,0.05); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">📦</div>
                    <div>
                        <h3 style="margin: 0; font-size: 1.1rem;">${product.name}</h3>
                        <small style="color: var(--text-muted); font-family: monospace;">${product.barcode}</small>
                    </div>
                </div>
                <div style="background: var(--bg-body); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
                    <p style="margin: 0; font-size: 0.9rem;">Brand: <strong>${brand ? brand.name : 'Unlisted'}</strong></p>
                </div>
                <div class="badges">
                    <span class="badge ${badgeClass}">${badgeText}</span>
                </div>
            </div>
        `;
    }

    static renderBarcodeResult(data) {
        const container = document.getElementById('barcode-result');
        const grid = document.getElementById('results-grid');
        grid.innerHTML = '';

        if (!data) {
            container.innerHTML = `
                <div class="card" style="text-align: center; border-top: 8px solid var(--danger); padding: 4rem 2rem;">
                    <div style="font-size: 4rem; margin-bottom: 2rem; filter: grayscale(1);">🔎</div>
                    <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">Data Missing</h2>
                    <p style="color: var(--text-muted); max-width: 400px; margin: 0 auto 3rem auto;">We haven’t indexed this barcode yet. Help the community by reporting it!</p>
                    <a href="#reports" class="btn btn-primary">Submit Missing Data</a>
                </div>
            `;
            container.style.display = 'block';
            return;
        }

        const isBoycotted = data.brand && data.brand.boycott_status;
        const statusColor = isBoycotted ? 'var(--danger)' : 'var(--success)';
        const bgLight = isBoycotted ? 'rgba(239, 68, 68, 0.05)' : 'rgba(16, 185, 129, 0.05)';
        const statusText = isBoycotted ? 'BOYCOTT FLAG' : 'ETHICAL CHOICE';
        const icon = isBoycotted ? '🚫' : '🛡️';

        let html = `
            <div class="card" style="border-top: 10px solid ${statusColor}; overflow: visible;">
                <div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); background: ${statusColor}; color: white; padding: 0.5rem 2rem; border-radius: 99px; font-weight: 800; letter-spacing: 0.1em; font-size: 0.8rem; box-shadow: var(--shadow-md);">
                    ${statusText}
                </div>
                
                <div style="text-align: center; margin-top: 1rem; margin-bottom: 3rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem; animation: tada 1s;">${icon}</div>
                    <h2 style="font-size: 2.25rem;">${data.product_name}</h2>
                    <p style="color: var(--text-muted); font-family: monospace; letter-spacing: 0.2em;">${data.barcode}</p>
                </div>

                <div style="background: ${bgLight}; padding: 2rem; border-radius: var(--radius-lg); margin-bottom: 3rem; border: 1px solid ${statusColor}22;">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <h4 style="margin: 0; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.1em; color: var(--text-muted);">Manufactured by</h4>
                    </div>
                    <h3 style="margin-bottom: 0.5rem;">${data.brand ? data.brand.name : 'Unknown Brand'}</h3>
                    ${isBoycotted ? `<p style="color: var(--danger); font-weight: 500; font-size: 1.1rem;">${data.brand.reason}</p>` : '<p style="color: var(--success); font-weight: 500;">Approved by community consensus for ethical distribution.</p>'}
                </div>
        `;

        if (data.alternatives && data.alternatives.length > 0) {
            html += `
                <div style="border-top: 1px solid var(--border); padding-top: 2rem;">
                    <h4 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="3"><path d="m12 15 2 2 4-4"/><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/></svg>
                        Ethical Recommendations
                    </h4>
                    <div style="display: grid; gap: 1rem;">
                        ${data.alternatives.map(alt => {
                // Backend BrandAlternative model has 'note' and 'score'
                return `
                                <div class="alternative-card">
                                    <div style="display: flex; flex-direction: column;">
                                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                                            <strong style="font-size: 1.1rem;">${alt.name}</strong>
                                            <span class="badge badge-success" style="font-size: 0.65rem;">Approved</span>
                                        </div>
                                        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
                                            ${alt.note || 'A local/ethical alternative with similar quality.'}
                                        </p>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color: var(--success); font-weight: 800; font-size: 0.8rem;">RELIABILITY</div>
                                        <div style="display: flex; gap: 2px; margin-top: 4px;">
                                            ${Array.from({ length: 5 }).map((_, i) => `<span style="width: 12px; height: 4px; background: ${i < (alt.score / 20) ? 'var(--success)' : 'rgba(0,0,0,0.1)'}; border-radius: 1px;"></span>`).join('')}
                                        </div>
                                    </div>
                                </div>
                            `;
            }).join('')}
                    </div>
                </div>
            `;
        } else if (isBoycotted) {
            html += `
                <div style="background: var(--bg-body); padding: 1.5rem; border-radius: var(--radius-md); text-align: center;">
                    <p style="color: var(--text-muted); margin: 0;">No specific alternatives verified for this item yet. Search by category for broader options.</p>
                </div>
            `;
        }

        html += `</div>`;

        container.innerHTML = html;
        container.style.display = 'block';
    }

    static renderBrands(brands) {
        const grid = document.getElementById('results-grid');
        const barcodeResult = document.getElementById('barcode-result');
        if (barcodeResult) barcodeResult.style.display = 'none';

        if (!brands || brands.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">No brands found matching your criteria.</div>';
            return;
        }
        grid.innerHTML = brands.map(brand => UI.renderBrandCard(brand)).join('');
    }

    static renderProducts(products) {
        const grid = document.getElementById('results-grid');
        const barcodeResult = document.getElementById('barcode-result');
        if (barcodeResult) barcodeResult.style.display = 'none';

        if (!products || products.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">No products found matching your criteria.</div>';
            return;
        }
        grid.innerHTML = products.map(p => UI.renderProductCard(p)).join('');
    }

    static renderReports(reports) {
        const list = document.getElementById('reports-list');
        if (!reports || reports.length === 0) {
            list.innerHTML = '<div class="card" style="text-align: center; color: var(--text-muted);">No activity recorded yet.</div>';
            return;
        }

        list.innerHTML = reports.map(r => `
            <div class="card" style="padding: 1.5rem; border-left: 4px solid ${getStatusColor(r.status)}; transition: none; transform: none; box-shadow: var(--shadow-sm);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-muted)"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        <strong style="font-size: 1.1rem;">${r.product ? r.product.name : (r.barcode || 'Anonymous Product')}</strong>
                    </div>
                    <span class="badge" style="background: ${getStatusLightColor(r.status)}; color: ${getStatusColor(r.status)}; border: 1px solid ${getStatusColor(r.status)}22;">${r.status}</span>
                </div>
                <p style="margin-bottom: 1.5rem; font-size: 0.95rem;">${r.message}</p>
                
                <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="width: 20px; height: 20px; border-radius: 50%; background: #e2e8f0; display: inline-flex; align-items: center; justify-content: center; font-size: 0.6rem; color: #475569;">👤</span>
                            User #${r.user_id}
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
                            ${new Date(r.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </div>
                    </div>
                    ${r.evidence_url ? `<a href="${r.evidence_url}" target="_blank" class="btn btn-outline" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; border-radius: 99px;">View Evidence</a>` : ''}
                </div>

                ${Auth.isAdmin() ? `
                <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem; border-top: 1px solid var(--border); padding-top: 1rem;">
                    <button class="btn btn-primary" style="padding: 0.4rem 1rem; font-size: 0.8rem; flex: 1;" onclick="app.updateReport(${r.id}, 'approved')">Verify & Approve</button>
                    <button class="btn btn-outline" style="padding: 0.4rem 1rem; font-size: 0.8rem; flex: 1; color: var(--danger); border-color: var(--danger);" onclick="app.updateReport(${r.id}, 'rejected')">Reject Report</button>
                </div>
                ` : ''}
            </div>
        `).join('');
    }

    static renderCategories(categories) {
        const filterSelect = document.getElementById('category-filter');
        const modalSelect = document.getElementById('brand-category');

        const options = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

        if (filterSelect) {
            const currentVal = filterSelect.value;
            filterSelect.innerHTML = '<option value="">All Categories</option>' + options;
            filterSelect.value = currentVal;
        }

        if (modalSelect) {
            modalSelect.innerHTML = '<option value="">Select Category...</option>' + options;
        }
    }

    static updateAuthUI() {
        const isLoggedIn = Auth.isLoggedIn();
        const user = Auth.getUser();
        const nav = document.querySelector('.nav');
        const authNav = document.getElementById('auth-nav');
        const reportsLink = document.getElementById('reports-link');

        if (!authNav) return;

        if (reportsLink) {
            reportsLink.style.display = isLoggedIn ? 'inline-block' : 'none';
        }

        authNav.innerHTML = '';
        nav.querySelectorAll('.dynamic-dashboard').forEach(el => el.remove());

        if (isLoggedIn) {
            if (user && user.role === 'admin') {
                reportsLink.insertAdjacentHTML('afterend', `<a href="#admin" class="dynamic-dashboard">Admin</a>`);
            }

            authNav.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem; background: var(--bg-body); padding: 0.25rem 0.5rem 0.25rem 1rem; border-radius: 99px; border: 1px solid var(--border);">
                    <span style="font-size: 0.85rem; font-weight: 600;">${user.username}</span>
                    <button onclick="Auth.logout()" class="btn btn-primary" style="padding: 0.35rem 1rem; font-size: 0.8rem; border-radius: 99px;">Logout</button>
                </div>
            `;
        } else {
            authNav.innerHTML = `
                <a href="#login" id="login-link">Sign In</a>
                <a href="#register" id="register-link" class="btn btn-primary" style="padding: 0.5rem 1.25rem; font-size: 0.9rem;">Join Now</a>
            `;
        }

        // Active state for nav
        const hash = window.location.hash || '#home';
        document.querySelectorAll('.nav a').forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === hash);
        });
    }

    static renderStats(stats) {
        const container = document.getElementById('admin-stats');
        if (!container) return;

        container.innerHTML = `
            <div class="card" style="text-align: center; border-bottom: 4px solid var(--primary);">
                <div style="font-size: 0.8rem; font-weight: 800; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 0.5rem;">BRANDS INDEXED</div>
                <h3 style="font-size: 3rem; color: var(--primary); margin: 0;">${stats.brands || 0}</h3>
            </div>
            <div class="card" style="text-align: center; border-bottom: 4px solid var(--secondary);">
                <div style="font-size: 0.8rem; font-weight: 800; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 0.5rem;">CATEGORIES</div>
                <h3 style="font-size: 3rem; color: var(--secondary); margin: 0;">${stats.categories || 0}</h3>
            </div>
            <div class="card" style="justify-content: center;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                    <button class="btn btn-primary" onclick="app.openBrandModal()">Add Brand</button>
                    <button class="btn btn-outline" onclick="app.openCategoryModal()">Categories</button>
                    <button class="btn btn-outline" style="grid-column: span 2;" onclick="window.location.hash='#reports'">Moderate Reports</button>
                </div>
            </div>
        `;
    }

    static renderCategoriesManage(categories) {
        const list = document.getElementById('categories-manage-list');
        if (!list) return;

        if (categories.length === 0) {
            list.innerHTML = '<p style="text-align:center; padding: 2rem; color: var(--text-muted);">No categories available.</p>';
            return;
        }

        list.innerHTML = categories.map(c => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: var(--bg-body); border-radius: var(--radius-md); margin-bottom: 0.5rem; border: 1px solid var(--border);">
                <span style="font-weight: 600;">${c.name}</span>
                <button class="btn btn-outline" style="padding: 0.4rem; color: var(--danger); border-color: transparent;" onclick="alert('Delete functionality is being updated.')">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
            </div>
        `).join('');
    }
}

function getStatusColor(status) {
    if (status === 'approved') return '#10b981';
    if (status === 'rejected') return '#ef4444';
    return '#f59e0b';
}

function getStatusLightColor(status) {
    if (status === 'approved') return 'rgba(16, 185, 129, 0.1)';
    if (status === 'rejected') return 'rgba(239, 68, 68, 0.1)';
    return 'rgba(245, 158, 11, 0.1)';
}

