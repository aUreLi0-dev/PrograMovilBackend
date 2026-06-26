import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { Button, Col, Container, Form, Row } from 'react-bootstrap';
import './ContactPage.css';

class ContactPage extends Component {
  constructor(props) {
    super(props);
    // Estado inicial del componente
    this.state = { };
  }
  // Método del ciclo de vida que se ejecuta después de que el componente se monta
  componentDidMount() {
    console.log('Componente montado');
    document.title = 'Contáctenos';
  }
    // Método del ciclo de vida que se ejecuta justo antes de que el componente se desmonte
  componentWillUnmount() {
    console.log('Componente a punto de desmontarse');
  }
  render() {
    return (
      <Container className="my-5 contacto-container">
      <Row className="align-items-center">
        {/* Texto a la izquierda */}
        <Col md={6}>
          <h1 className="fw-bold">Es momento de cambiar tu realidad</h1>
          <p className="lead">Sé un líder en el mercado laboral</p>
        </Col>

        {/* Formulario a la derecha */}
        <Col md={6}>
          <div className="form-section">
            <Form>
              <Form.Group className="mb-3" controlId="nombre">
                <Form.Label>Nombres*</Form.Label>
                <Form.Control type="text" placeholder="Nombres" required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="apellidos">
                <Form.Label>Apellidos*</Form.Label>
                <Form.Control type="text" placeholder="Apellidos" required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="correo">
                <Form.Label>Correo Electrónico*</Form.Label>
                <Form.Control type="email" placeholder="Correo Electrónico" required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="celular">
                <Form.Label>Celular*</Form.Label>
                <Form.Control type="tel" placeholder="Celular" required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="sede">
                <Form.Label>Sede de interés*</Form.Label>
                <Form.Select required>
                  <option value="">Seleccionar</option>
                  <option value="sede1">Sede 1</option>
                  <option value="sede2">Sede 2</option>
                  <option value="sede3">Sede 3</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3" controlId="carrera">
                <Form.Label>Carrera de interés*</Form.Label>
                <Form.Select required>
                  <option value="">Seleccionar</option>
                  <option value="carrera1">Carrera 1</option>
                  <option value="carrera2">Carrera 2</option>
                  <option value="carrera3">Carrera 3</option>
                </Form.Select>
              </Form.Group>

              <Form.Check 
                type="checkbox" 
                label="He leído y acepto las Políticas de Privacidad" 
                required 
                className="mb-2" 
                id="politicas"
              />

              <Form.Check 
                type="checkbox" 
                label="Autorizo el envío de publicidad e información comercial." 
                className="mb-3" 
                id="publicidad"
              />

              <Button type="submit" variant="success" className="w-100">ENVIAR</Button>
            </Form>
          </div>
        </Col>
      </Row>
    </Container>
    );
  }
}
export default ContactPage;
