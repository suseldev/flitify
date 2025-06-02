import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Computers from './pages/computers/computers.jsx'
import Interact from './pages/interact/interact.jsx';
import Layout from './pages/layout/layout.jsx';
import Login from './pages/login/login.jsx';
import LogoutHandler from './pages/logout/logout.jsx'
import { useAuth } from './hooks/useAuth.jsx';
import './App.css';

const AuthProtected = ({ children }) => {
  const { isAuthenticated } = useAuth();

  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
		<Route path="/" element={<AuthProtected><Layout /></AuthProtected>}>
			<Route path="/interact" element={<Interact />} />
			<Route path="/computers" element={<Computers />} />
			<Route path="/logout" element={<LogoutHandler />} />
			<Route path="*" element={<Navigate to="/interact" replace />} />
		</Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
