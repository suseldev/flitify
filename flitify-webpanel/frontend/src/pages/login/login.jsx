import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './login.css';

function Login() {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState(null);
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError(null);

		try {
			const res = await fetch('/api/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password }),
			});
			const data = await res.json();

			if (data.login_status === 'ok' && data.token) {
				localStorage.setItem('token', data.token);
				navigate('/interact');
			} else {
				if(data.login_status == 'invalid_credentials') {
					setError('invalid username or password');
					return;
				}
				setError(data.login_status || 'unknown error');
			}
		} catch (err) {
			setError('network error');
		}
	};

	return (
		<div className="login-page">
			<form className="login-form" onSubmit={handleSubmit}>
				<div className="text-container">
					<span className="flitify-name">Flitify</span>
					<span className="page-name">Sign in</span>
				</div>
				<input
					type="text"
					placeholder="Username"
					value={username}
					onChange={(e) => setUsername(e.target.value)}
				/>
				<input
					type="password"
					placeholder="Password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
				/>
				<button type="submit">Log In</button>
				{error && <p className="error-msg">Error while signing in:<br/>{error}</p>}
			</form>
		</div>
	);
}

export default Login;
