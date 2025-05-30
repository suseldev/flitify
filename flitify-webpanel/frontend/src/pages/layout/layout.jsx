import { useState } from 'react';
import Navbar from '../../Components/Navbar.jsx'

function Layout() {
	const [currentView, setCurrentView] = useState('')
	
	return (
		<>
			<Navbar currentView={currentView}/>
		</>
	)
}

export default Layout;
