import { useEffect, useState } from 'react';
import fetchWithAuth from '../../utils/fetchWithAuth.js'
import { Eye } from 'lucide-react';
import './computers.css';

function Computers() {
	const [clients, setClients] = useState([]);
	const [error, setError] = useState(null);
	const [loading, setLoading] = useState(true);
	const [visibleSecrets, setVisibleSecrets] = useState({});
	const [refreshKey, setRefreshKey] = useState(0)
	useEffect(() => {
		fetchWithAuth('/api/allclients')
			.then(res => res.json())
			.then(data => {
				setClients(data.clients || []);
				setLoading(false);
			})
			.catch(() => {
				setError('Failed to load clients');
				setLoading(false);
			});
	}, [refreshKey]);

	const toggleSecret = (id) => {
		setVisibleSecrets(prev => ({
			...prev,
			[id]: !prev[id]
		}));
	};

	const deleteClient = (id) => {
		if (!window.confirm(`Delete client "${id}"?`)) return;
		fetchWithAuth(`/api/allclients/${id}`, { method: 'DELETE' })
			.then(() => setClients(prev => prev.filter(c => c.client_id !== id)))
			.catch(() => alert('Failed to delete client.'));
	};

	const regenerateSecret = (id) => {
		const newSecret = prompt(`New secret for ${id}?`);
		if (!newSecret) return;
		fetchWithAuth(`/api/allclients/${id}`, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ secret: newSecret })
		})
		.then(() => {
			setClients(prev =>
				prev.map(c => c.client_id === id ? { ...c, secret: newSecret } : c)
			);
		})
		.catch(() => alert('Failed to update secret.'));
	};


	const addNewClient = () => {
		const client_id = prompt("Enter new client ID:");
		if (!client_id) return;
		const secret = prompt("Enter secret for new client:");
		if (!secret) return;

		fetchWithAuth('/api/allclients', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ client_id, secret })
		})
		.then(async res => {
			const rjson = await res.json();
			if (res.status === 409) {
				alert("Client already exists.");
				return;
			}
			if (res.status !== 201 || rjson.proxy_status !== 'ok') {
				alert("Failed to add client.");
				return;
			}
			// refresh
			setRefreshKey(1);
		})
		.catch(() => alert("Error adding client."));
	};

	if (loading) return <div className="loading">Loading...</div>;

	return (
		<div className="computers-page">
			<div className="page-header">
				<span className="page-name">Registered clients list</span>
				<a href="" className="add-button" onClick={(e) => {e.preventDefault(); addNewClient();}}>+ Add new client</a>
			</div>
			{error && <p className="error-msg">{error}</p>}
			<table className="computers-table">
				<thead>
					<tr>
						<th>Client ID</th>
						<th>Secret</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{clients.map(({ client_id, secret }) => (
						<tr key={client_id}>
							<td className="clientid">{client_id}</td>
							<td className="secret">
								<div className="secret-container">
									{visibleSecrets[client_id] ? secret : '(hidden)'}{' '}
									<Eye className="show-button" size={18} onClick={() => toggleSecret(client_id)} />
								</div>
							</td>
							<td className="actions">
								<a href="#" className="delete" onClick={(e) => { e.preventDefault(); deleteClient(client_id); }}>Delete</a>{' '}
								<a href="#" onClick={(e) => { e.preventDefault(); regenerateSecret(client_id); }}>Change secret</a>
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
}

export default Computers;
