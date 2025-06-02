import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

function LogoutHandler() {
	const navigate = useNavigate();
	const { logout } = useAuth();

	useEffect(() => {
		logout();
		navigate('/login');
	}, [logout, navigate]);

	return null;
}

export default LogoutHandler;
