import React, { Component } from 'react';
import { Button, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import './AboutUsPage.css';

class AboutUsPage extends Component {
    constructor(props) {
    super(props);
        // Estado inicial del componente
        this.state = { };
    }

    incrementarContador = () => {
    };

    // Método del ciclo de vida que se ejecuta después de que el componente se monta
    componentDidMount() {
        console.log('Componente montado');
        document.title = 'Más sobre nosotros';
    }
    // Método del ciclo de vida que se ejecuta justo antes de que el componente se desmonte
    componentWillUnmount() {
        console.log('Componente a punto de desmontarse');
    }
    render() {
    return (
      <div className="video-container">
      {/* Video de fondo */}
      <video className="video-background" autoPlay muted loop>
        <source src="/video/vegueta.mp4" type="video/mp4" />
        Tu navegador no soporta la reproducción de videos.
      </video>

      {/* Capa de contenido sobre el video */}
      <div className="content-overlay">
        <Container className="d-flex justify-content-center align-items-center vh-100 text-center text-white">
          <div>
            <h1 className="display-4">Bienvenido a Nuestro Sitio</h1>
            <p className="lead">Explora y descubre contenido increíble mientras disfrutas de este fondo visual.</p>
            <Button variant="primary" href="#">Explorar Más</Button>
          </div>
        </Container>
      </div>
    </div>
    );
  }
}
export default AboutUsPage;
