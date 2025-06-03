import { useEffect, useState } from 'react';
import fetchWithAuth from '../../../utils/fetchWithAuth.js';
import './shell.css'



function Shell( {clientId} ) {
	const [history, setHistory] = useState(`Welcome to Flitify pseudo-interactive shell for client ${clientId}`);
	const [inputValue, setInputValue] = useState('');
	const [pending, setPending] = useState(false);

	function handleCommand(cmd) {
		setHistory(history + `\n\$ ${cmd}\n` + 'Waiting for response...');
		setInputValue('');
		setPending(true)
		fetchWithAuth(`/api/proxy/${clientId}/shellcommand?cmd=${encodeURIComponent(cmd)}`).then(res => res.json()).then(data => {
			if(data.proxy_status !== 'ok') throw new Error('Bad response')
			const stdout = data.command_response?.stdout || '';
			const stderr = data.command_response?.stderr || '';

			let output = '';
			if (stdout) output += stdout.trim();
			if (stderr) output += `\n[STDERR]\n${stderr.trim()}`;
			setHistory(history + `\n\$ ${cmd}\n` + output);
			setPending(false)
		}).catch(() => {
			setHistory(history + `\n\$ ${cmd}\n` + 'Failed to execute command')	
			setPanding(false)
		});
		
	}

	function handleKeyDown(e) {
		if (e.key === 'Enter' && inputValue.trim() !== '') {
			e.preventDefault();
			handleCommand(inputValue.trim());
		}
	}
	return (
		<div className="shell">
			<div className="shell-card">
				<div className="terminal">
					{history}
				</div>
				<div className="command-input">	
					<span className="prompt">{`flitify (${clientId}) > `}</span>
					<input type="text" placeholder={`${pending ? 'waiting...' : 'command...'}`} value={inputValue} onChange={e => setInputValue(e.target.value)} onKeyDown={handleKeyDown} disabled={pending}/>
				</div>
			</div>
		</div>
	)
}

export default Shell;
