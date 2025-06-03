import { useState, useEffect } from 'react';
import { ChevronRight, CircleX } from 'lucide-react';
import fetchWithAuth from '../../utils/fetchWithAuth.js'
import Navbar from '../../Components/Navbar.jsx'
import StatusDashboard from './components/statusdashboard.jsx'
import Files from './components/files.jsx'
import './interact.css'

function Interact() {
	const [clients, setClients] = useState([]);
	const [selectedClient, setSelectedClient] = useState(null);
	const [menuOpen, setMenuOpen] = useState(true);
	const [selectedTab, setSelectedTab] = useState('Status');
	const tabs = ['Status', 'Files', 'Shell'];
	const [error, setError] = useState(null);

	useEffect(() => {
		fetchWithAuth('/api/proxy/clients')
			.then(res => res.json())
			.then(data => {
				if(data['proxy_status'] != 'ok' || data['status'] != 'ok') {
					setError('Failed to fetch clients.')
				}
				setClients(data['client_list']);
			})
			.catch(err => setError('Failed to fetch clients.'));
	}, []);

	return (
		<>
			<div className="view-main">
				<div className={`sidebar ${menuOpen? 'show' : ''}`}>
					<span className="header">Online clients</span>
					<ul className="pc-list">
						{clients.map((id) => (
							<li key={id}>
								<a href="#" className={selectedClient === id ? 'active' : ''} onClick={() => {setSelectedClient(id); setMenuOpen(false)}}>{id}</a>
							</li>
						))}
					</ul>
					{error && <div className="error-msg">
						<CircleX />
						<span>{error}</span>
						</div>}
				</div>

				<div className="dashboard">

					{selectedClient ? (
					<>
						<div className="tab-bar">
							{tabs.map((tab) => (
							<button key={tab} className={`tab-button ${selectedTab === tab ? 'active' : ''}`} onClick={() => setSelectedTab(tab)}> {tab.charAt(0).toUpperCase() + tab.slice(1)}</button>
							))}
						</div>
						{selectedTab === "Status" && <StatusDashboard clientId={selectedClient} />}
						{selectedTab === "Files" && <Files clientId={selectedClient} />}
					</> ) : (
						<div className="client-placeholder">
							<p>Select a client to get started...</p>
						</div>
					)
					}
				</div>
			</div>
			{!menuOpen && (
				<button className="sidebar-toggle" onClick={() => setMenuOpen(true)}><ChevronRight /></button>
			)}
		</>
	);
}

export default Interact;
