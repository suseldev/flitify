export default async function fetchWithAuth(url, options = {}) {
	console.log('fetch with auth')
	const token = localStorage.getItem('token');
	const headers = {
		...options.headers,
		Authorization: `Bearer ${token}`,
		'Content-Type': 'application/json',
	};
	const response = await fetch(url, {
		...options,
		headers,
	});
	if (response.status === 401 || response.status === 403) {
		localStorage.removeItem('token');
		window.location.href = '/login';
		throw new Error('Unauthorized');
	}

	return response;
}
