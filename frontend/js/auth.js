class Auth {
    static isLoggedIn() {
        return !!localStorage.getItem('boycott_token');
    }

    static getUser() {
        const userStr = localStorage.getItem('boycott_user');
        return userStr ? JSON.parse(userStr) : null;
    }

    static isAdmin() {
        const user = Auth.getUser();
        return user && user.role === 'admin';
    }

    static async login(email, password) {
        const response = await API.login(email, password);
        localStorage.setItem('boycott_token', response.access_token);
        localStorage.setItem('boycott_user', JSON.stringify(response.user));
        window.dispatchEvent(new Event('auth-change'));
        return response.user;
    }

    static logout() {
        localStorage.removeItem('boycott_token');
        localStorage.removeItem('boycott_user');
        window.dispatchEvent(new Event('auth-change'));
        window.location.hash = '#home';
    }
}
