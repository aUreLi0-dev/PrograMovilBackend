import React, { Component } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import InputText from './InputText.jsx';
import './NavBar.css';

class Footer extends Component {
  constructor(props) {
    super(props);
    // Estado inicial del componente
    this.state = { 
      email: '', validEmail: null,
      message: '', validMessage: null,
      disabled: true,
    };
    this.inputEmailRef = React.createRef(); 
  }

  incrementarContador = () => {
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

  validateEmail = () => {
    const { email } = this.state;
    const regex = /^[a-zA-Z0-9._%+-]+@certus\.edu\.pe$/;
    if(email != ''){
      this.setState({validEmail: regex.test(email)});
    }else{
      this.setState({validEmail: null})
    }
  }

  validateMessage = () => {
    const { message } = this.state;
    console.log(message)
    if(message != ''){
      if(message.length > 0 && message.length <= 20){
        this.setState({validMessage: true});
      }else{
        this.setState({validMessage: false});
      }
    }else{
      this.setState({validMessage: null});
    }
  }

  handleChange = (e) => {
    this.setState(
      {[e.target.name]: e.target.value}
    , () => {
      const { email, message, disabled} = this.state;
      if(e.target.name == 'email'){this.validateEmail()}
      if(e.target.name == 'message'){this.validateMessage()}
    });
  }

  handleSubmit = (e) => {
    alert();
    e.preventDefault();
    const { email, message } = this.state;
    // Usar fetch para enviar la solicitud POST
    const data = {
      email: this.inputEmailRef.current.state.value,
      message: message,
    }
    fetch('/api/message', {
      method: 'POST', // Método HTTP
      headers: {
          'Content-Type': 'application/json' // Indicar que se envía JSON
        },
        body: JSON.stringify(data) // Convertir el objeto a JSON
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error en la solicitud: ${response.status}`);
        }
        alert();
        return response.json(); // Convertir la respuesta en JSON
      })
      .then(data => {
        console.log('Respuesta:', data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }

  handleValidationChange = (valid) => {
    this.setState({
      validEmail: valid,
    });
  };

  render() {
    const { email, message, validEmail, validMessage } = this.state;
  return (
    <footer className="bg-dark text-white pt-5">
      <Container>
        <Row>
          {/* Secciones de la página */}
          <Col md={4} className="mb-4">
            <h5>Secciones</h5>
            <ul className="list-unstyled">
              <li><Link to="/" className="text-white text-decoration-none">Home</Link></li>
              <li><Link to="/nosotros" className="text-white text-decoration-none">Nosotros</Link></li>
              <li><Link to="/servicios" className="text-white text-decoration-none">Servicios</Link></li>
              <li><Link to="/clientes" className="text-white text-decoration-none">Clientes</Link></li>
              <li><Link to="/contacto" className="text-white text-decoration-none">Contacto</Link></li>
            </ul>
          </Col>

          {/* Información de contacto */}
          <Col md={4} className="mb-4">
            {/* Información de contacto 
            <h5>Contacto</h5>
            <p>
              📍 Dirección: Calle Principal, 123<br />
              📞 Teléfono: +1 234 567 890<br />
              📧 Email: contacto@vegüeta.com
            </p>
            <p>Síguenos en:</p>
            <a href="#" className="text-white me-3"><i className="bi bi-facebook"></i></a>
            <a href="#" className="text-white me-3"><i className="bi bi-twitter"></i></a>
            <a href="#" className="text-white"><i className="bi bi-instagram"></i></a>
            */}
            <h5>Suscríbete</h5>
            <InputText 
              id="txtNombre"
              label="Nombre" 
              placeholder="Ingrese su nombre" 
              name="name"
              value=""
              onChangeValidations= {[
                {
                  type: 'maxLength',
                  validText: '',
                  invalidText: 'No puede tener más de 10 carecteres.',
                  max: 10
                },
              ]} 
              />
            <InputText 
              name = "email"
              label="Email" 
              placeholder="Ingrese su email"
              type="email" 
              onChangeValidations= {[
                {
                  type: 'email',
                  validText: 'Correo válido',
                  invalidText: 'Formato del correo no válido'
                },
                {
                  type: 'maxLength',
                  validText: '',
                  invalidText: 'Correo no puede pasar los 20 caracteres.',
                  max: 20
                },
                {
                  type: 'maxLengthdddd',
                  validText: '',
                  invalidText: 'Correo no puede pasar los 20 caracteres.',
                  max: 20
                },
                {
                  type: 'custom',
                  validText: '',
                  invalidText: 'Correo no puede pasar los 20 caracteres.',
                  def: () => {
                    alert();
                  }
                },
              ]}/>
            <InputText 
              label="Edad" 
              placeholder="Ingrese su edad"
              type="number"
              name="edad"/>
          </Col>

          {/* Formulario */}
          <Col md={4} className="mb-4">
            <h5>Suscríbete</h5>
            <Form onSubmit={this.handleSubmit} method="POST">
              <InputText 
                ref={this.inputEmailRef}
                name = "email"
                label="Email" 
                placeholder="Ingrese su email"
                type="email" 
                onValidationChange={this.handleValidationChange}
                onChangeValidations= {[
                  {
                    type: 'email',
                    validText: 'Correo válido',
                    invalidText: 'Formato del correo no válido'
                  },
                ]}/>
              <Form.Group className="mb-3" controlId="mensaje">
                <Form.Label>Mensaje {message.length} / 20</Form.Label>
                <Form.Control 
                  as="textarea" 
                  rows={3} 
                  placeholder="Escribe tu mensaje" 
                  name='message' 
                  value={message}
                  className={validMessage == null ? '': (validMessage ? 'is-valid': 'is-invalid')}
                  onChange={this.handleChange}/>
                {validMessage == null ? '' :
                  validMessage == true ?
                    <Form.Control.Feedback>
                      Mensaje válido
                    </Form.Control.Feedback>
                  : <Form.Control.Feedback type="invalid">  
                    Mensaja puede tener hasta 20 caracteres.
                  </Form.Control.Feedback>}
              </Form.Group>
              <Button 
                type="submit" 
                variant="primary" 
                className="w-100" 
                disabled={!validMessage || !validEmail}>
                Enviar
              </Button>
            </Form>
          </Col>
        </Row>
      </Container>

      {/* Línea divisoria y derechos reservados */}
      <div className="text-center bg-secondary py-3 mt-4">
        <p className="mb-0">© 2025 Végueta. Todos los derechos reservados.</p>
      </div>
    </footer>  
  );
  }
}
export default Footer;