import { useEffect, useState } from 'react';
import fetchWithAuth from '../../utils/fetchWithAuth.js'

function Computers() {
	const [clients, setClients] = useState([]);
	const [error, setError] = useState(null);

	useEffect(() => {
		const fetchClients = async () => {
			try {
				const res = await fetchWithAuth('/api/allclients');
				const data = await res.json();
				setClients(data.clients || []);
			} catch (err) {
				setError(err.message);
			}
		};

		fetchClients();
	}, []);

	return (
		<div className="computers-page">
			<span className="page-name">Registered clients list</span>
			{error && <p className="error-msg">{error}</p>}
			<ul className="computers-list">
				{clients.map(client => (
					<li key={client.client_id} className="client-entry">
						<span>{client.client_id}</span>
						<button onClick={() => alert(`Remove ${client.client_id}`)}>Remove</button>
					</li>
				))}
			</ul>
		</div>
	);
}

export default Computers;
