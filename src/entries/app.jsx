import { createRoot } from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../assets/styles/styles.css';
import App from '../components/layouts/App.jsx';

createRoot(document.getElementById('root')).render(
  <>
  <App />
  </>
)
