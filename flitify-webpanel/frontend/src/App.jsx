import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Interact from './pages/interact/interact.jsx';
import Layout from './pages/layout/layout.jsx';
import './App.css';

const AuthRedirect = () => {
  const isAuthenticated = true; // TODO: Replace with real logic

  return isAuthenticated ? (
    <Navigate to="/interact" replace />
  ) : (
    <Navigate to="/login" replace />
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AuthRedirect />} />
        <Route path="/interact" element={<Layout><Interact /></Layout>} />
        <Route path="/login" element={<div>Login Page</div>} /> {/* opcjonalna strona logowania */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
