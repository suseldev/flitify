export function useAuth() {
	const token = localStorage.getItem('token');

	function isAuthenticated() {
		if (!token) return false;

		const parts = token.split('.');
		if (parts.length !== 3) {
			logout();
			return false;
		}

		try {
			const payload = JSON.parse(atob(parts[1]));
			const now = Math.floor(Date.now() / 1000);
			if (!payload.exp || payload.exp < now) {
				logout();
				return false;
			}
			return true;
		} catch (e) {
			logout();
			return false;
		}
	}

	function login(newToken) {
		localStorage.setItem('token', newToken);
	}

	function logout() {
		localStorage.removeItem('token');
	}

	return { token, isAuthenticated, login, logout };
}
