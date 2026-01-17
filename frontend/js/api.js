const API_BASE = window.location.origin;

class API {
    static async request(endpoint, options = {}) {
        const token = localStorage.getItem('boycott_token');
        const headers = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...options.headers
        };

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'API Request Failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    static login(email, password) {
        return API.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    static register(username, email, password) {
        return API.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    }

    // Brands
    static getBrands(params = {}) {
        const query = new URLSearchParams(params).toString();
        return API.request(`/brands?${query}`);
    }

    static getBrand(id) {
        return API.request(`/brands/${id}`);
    }

    static createBrand(data) {
        return API.request('/brands', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static updateBrand(id, data) {
        return API.request(`/brands/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static deleteBrand(id) {
        return API.request(`/brands/${id}`, {
            method: 'DELETE'
        });
    }

    // Categories
    static getCategories() {
        return API.request('/categories');
    }

    // Products
    static getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return API.request(`/products?${query}`);
    }

    static getBarcode(barcode) {
        return API.request(`/barcode/${barcode}`);
    }

    // Reports
    static getReports(status = null) {
        const query = status ? `?status=${status}` : '';
        return API.request(`/reports${query}`);
    }

    static getMyReports() {
        return API.request('/reports/mine');
    }

    static createReport(data) {
        return API.request('/reports', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static updateReport(id, data) {
        return API.request(`/reports/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    static async getStats() {
        // In a real app, you'd want a dedicated endpoint.
        // For now, we'll fetch lists with low limits to get counts if the API returned counts, 
        // but since it doesn't return metadata with counts, we might have to fetch all (expensive) 
        // OR just show "Many" 
        // OR implementing a specific stats endpoint in backend would be better.
        // For this task, I'll rely on the existing "refreshStats" logic from the old app which fetched all.
        try {
            const [brands, categories] = await Promise.all([
                API.getBrands({ limit: 100 }),
                API.getCategories()
            ]);
            return {
                brands: brands.length,
                categories: categories.length
            };
        } catch (e) {
            return { brands: 0, categories: 0 };
        }
    }
}
