import { useEffect, useState } from 'react';
import { File, Folder, Upload } from 'lucide-react';
import fetchWithAuth from '../../../utils/fetchWithAuth.js';
import './files.css';

function downloadFile(clientId, entry, currentPath) {
	const filePath = currentPath + (currentPath.endsWith('/') ? '' : '/') + entry.name;
	const url = `/api/proxy/${clientId}/getfile?file_path=${encodeURIComponent(filePath)}`;
	
	fetchWithAuth(url)
		.then(response => {
			if (!response.ok) throw new Error('Failed to download');
			return response.blob();
		})
		.then(blob => {
			const link = document.createElement('a');
			link.href = URL.createObjectURL(blob);
			link.download = entry.name;
			document.body.appendChild(link);
			link.click();
			link.remove();
		})
		.catch(() => {
			alert('Failed to download file');
		});
}

function getParentPath(path) {
  if (path.length > 1 && path.endsWith('/')) {
    path = path.slice(0, -1);
  }

  const lastSlashIndex = path.lastIndexOf('/');
  return lastSlashIndex > 0 ? path.substring(0, lastSlashIndex) : '/';
}

function Files({clientId}) {
	const [currentPath, setCurrentPath] = useState('/');
	const [files, setFiles] = useState({});
	const [error, setError] = useState(null)
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		if (!clientId || !currentPath) return;
		setLoading(true);
		fetchWithAuth(`/api/proxy/${clientId}/listdir?path=${encodeURIComponent(currentPath)}`)
			.then(res => res.json())
			.then(data => {
				if (data.proxy_status !== 'ok') throw new Error();
				setFiles(data.entries);
				setLoading(false);
			})
			.catch(() => {
				setFiles([]);
				setError('Cannot load files');
				setLoading(false);
			});
	}, [clientId, currentPath]);

	if (error) return <div className="error-msg"><CircleX size={64}/> <span>{error}</span></div>;
	if (loading) return <div className="loading">Loading...</div>;

	return(
		<div className="filebrowser-wrapper">	
			<div className="filebrowser">
				<span className="name">File browser</span>
				<div className="files-header">
					<span className="path">{currentPath}</span>
					<label className="upload-button">
						<Upload size={14} style={{ marginRight: '4px' }} />
						Upload file
						<input type="file" style={{ display: 'none' }} onChange={(e) => {
							const file = e.target.files[0];
							if (!file) return;
						
							const formData = new FormData();
							formData.append('file', file);
							console.log(file)
							formData.append('path', currentPath + '/' + file.name);
						
							fetchWithAuth(`/api/proxy/${clientId}/uploadfile`, {
								method: 'POST',
								body: formData
							})
							.then(() => {
								setCurrentPath(currentPath);
							});
						}} />
					</label>
				</div>
				<div className="entries">
					<ul className="file-list">
						{currentPath !== '/' && (
							<li className="file-item dir" onClick={() => {
								setCurrentPath(getParentPath(currentPath));
							}}>
								<Folder size={18} />
								<span>..</span>
							</li>
						)}
						{files.map((entry, i) => (
							<li key={i} className={`file-item ${entry.type == 'dir' ? 'dir' : ''}`} onClick={() => {
								if (entry.type == 'dir'){
									setCurrentPath(prev => prev.endsWith('/') ? prev + entry.name : prev + '/' + entry.name);
								} else {
									downloadFile(clientId, entry, currentPath);
								};
							}}>
								{entry.type == 'dir' ? <Folder size={18} /> : <File size={18} />}
								<span>{entry.name}</span>
							</li>
						))}
					</ul>
				</div>
			</div>
		</div>
	);
}

export default Files;
