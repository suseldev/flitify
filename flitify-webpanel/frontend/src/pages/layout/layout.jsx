import { useState } from 'react';
import Navbar from '../../Components/Navbar.jsx';
import { Outlet } from 'react-router-dom';
import './layout.css';

function Layout() {
	const [currentView, setCurrentView] = useState('');
	
	return (
		<>
			<Navbar currentView={currentView}/>
			<main className="page-content">
				<Outlet />
			</main>
		</>
	);
}

export default Layout;
