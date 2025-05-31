import { useState } from 'react';
import Navbar from '../../Components/Navbar.jsx'
import './interact.css'

function Interact() {
	return (
		<>
			<div className="view-main">
				<div className="sidebar">
					<span class="header">Online clients</span>
					<ul class="pc-list">
						<li><a href="#" className="active">PC-1</a></li>	
						<li><a href="#">PC-2</a></li>	
						<li><a href="#">PC-3</a></li>	
						<li><a href="#">PC-4</a></li>	
						<li><a href="#">PC-5</a></li>	
					</ul>
				</div>
				<div className="dashboard">
					<p>Dashboard content goes here</p>
				</div>
			</div>
		</>
	)
}

export default Interact;
