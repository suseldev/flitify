import { useEffect, useState } from 'react';
import { CircleX } from 'lucide-react';
import fetchWithAuth from '../../../utils/fetchWithAuth.js';
import './statusdashboard.css';

function StatusModule({ clientId }) {
	const [status, setStatus] = useState(null);
	const [error, setError] = useState(null);

	useEffect(() => {
		if (!clientId) return;

		fetchWithAuth(`/api/proxy/${clientId}/status`)
			.then(res => res.json())
			.then(data => {
				if (data.proxy_status !== 'ok') throw new Error('API error');
				setStatus(data[clientId]);
			})
			.catch(() => setError('Failed to load status'));
	}, [clientId]);

	if (error) return <div className="error-msg"><CircleX size={64}/> <span>{error}</span></div>;
	if (!status) return <div className="loading">Loading...</div>;

	const uptime = convertUptime(status.uptime_seconds);
	const user = status.current_user;
	const cpu = status.cpu_usage;
	const ramPercent = Math.round((status.memory_used / status.memory_total) * 100);

	const diskEntries = Object.entries(status.disks);
	const appEntries = Object.entries(status.running_applications);

	return (
		<div className="status">
			<div className="status-grid">
				<div className="status-card">
					<h3>System information</h3>
					<p><span className="parameter">Uptime:</span> {uptime}</p>
					<p><span className="parameter">Currently logged user:</span> {user}</p>
					<p><span className="parameter">CPU usage:</span> {cpu}%</p>
					<p><span className="parameter">Memory usage:</span> {ramPercent}% ({status.memory_used} / {status.memory_total} GiB)</p>
				</div>

				<div className="status-card">
					<h3>Disks usage</h3>
					{diskEntries.map(([disk, info]) => {
						const percent = Math.round((info.used / info.total) * 100);
						return (
							<p key={disk}>
								<span className="parameter">{disk}:</span> {percent}% ({info.used}/{info.total} GB)
							</p>
						);
					})}
				</div>

				<div className="status-card full">
					<h3>Running applications</h3>
					<ul className="process-list">
						{appEntries.map(([proc, info]) => (
							<li key={proc}>
								<span className="parameter">{info.name} ({info.open_windows}):</span> {proc}
							</li>
						))}
					</ul>
				</div>
			</div>
		</div>
	);
}

function convertUptime(seconds) {
	const d = Math.floor(seconds / 86400);
	const h = Math.floor((seconds % 86400) / 3600);
	const m = Math.floor((seconds % 3600) / 60);
	return `${d > 0 ? d + 'd ' : ''}${h}h ${m}m`;
}

export default StatusModule;
