import React, { Component } from 'react';
import { Container, Form, Button, Row, Col, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import './HomePage.css';

class HomePage extends Component {
  constructor(props) {
    super(props);
    // Estado inicial del componente
    this.state = {
      contador: 0
    }; 
  }

  // Método para manejar el incremento del contador
  incrementarContador = () => {
    this.setState({ contador: this.state.contador + 1 });
  };

  // Método del ciclo de vida que se ejecuta después de que el componente se monta
  componentDidMount() {
    console.log('Componente montado');
    document.title = 'Ingresar a la Aplicación';
  }

  // Método del ciclo de vida que se ejecuta justo antes de que el componente se desmonte
  componentWillUnmount() {
    console.log('Componente a punto de desmontarse');
  }

  render() {
    return (
      <div className="login-container">
        <Container>
          <Row className="justify-content-md-center">
            <Col xs={12} md={4} className="login-form">
              <h2>Iniciar Sesión</h2>
              <Form>
                <Form.Group className="mb-3" controlId="formBasicEmail">
                  <Form.Label>Usuario</Form.Label>
                  <Form.Control type="email" placeholder="Ingresa tu usuario" />
                </Form.Group>

                <Form.Group className="mb-3" controlId="formBasicPassword">
                  <Form.Label>Contraseña</Form.Label>
                  <Form.Control type="password" placeholder="Contraseña" />
                </Form.Group>

                <Button variant="primary" type="submit">
                  Iniciar Sesión
                </Button>
              </Form>
              <div className="mt-3">
                <Nav.Link as={Link} to="/sign-up">¿No tienes cuenta? Regístrate</Nav.Link>
                <Nav.Link as={Link} to="/reset-password">Olvidé mi contraseña</Nav.Link>
              </div>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}

export default HomePage;
