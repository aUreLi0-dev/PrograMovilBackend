import { createRoot } from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../assets/styles/styles.css';
import Web from '../components/layouts/Web.jsx';

createRoot(document.getElementById('root')).render(
  <>
  <Web />
  </>
)
