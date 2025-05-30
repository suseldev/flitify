import './Navbar.css';
import { useState } from 'react';
import { ChevronDown, Menu } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom'

function Navbar(args) { 
	const currentLocation = useLocation();
	const currentView = currentLocation.pathname.split("/").filter(Boolean)[0] || "";;
	const [menuOpen, setMenuOpen] = useState(false);

	return (
		<>
    <nav className={`navbar ${menuOpen ? 'active':''}`} id="navbar">
        <div className="logo">
					<button className="hamburger" onClick={() => setMenuOpen(prev => !prev)}>
						<Menu size={24} />
					</button>
			<span className="flitify">Flitify</span>
		</div>
        <ul id="navbar-links">
			<li><Link to="/interact" className={`navbar-link ${currentView=='interact' ? 'active':''} `}>Interact</Link></li>
			<li><Link to="/computers" className={`navbar-link ${currentView=='computers' ? 'active':''}`}>Computers</Link></li>
        </ul>
		<a className="user" href="#">User1 <ChevronDown size={16} /> </a>
    </nav>
		</>
	)
}
export default Navbar
