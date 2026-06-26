import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import './NavBar.css';

class NavBar extends Component {
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
        document.title = 'Ingresar a la Aplicación';
    }
    // Método del ciclo de vida que se ejecuta justo antes de que el componente se desmonte
    componentWillUnmount() {
        console.log('Componente a punto de desmontarse');
    }
    render() {
        return (
            <Navbar bg="dark" variant="dark" expand="lg" fixed="top">
                <Container>
                    <Navbar.Brand href="#">Végueta</Navbar.Brand>
                    <Navbar.Toggle aria-controls="navbarNav" />
                    <Navbar.Collapse id="navbarNav">
                        <Nav className="ms-auto">
                            <Nav.Item>
                                <Link to="/" className="nav-link">Home</Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Link to="/nosotros" className="nav-link">Nosotros</Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link href="#">Servicios</Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link href="#">Clientes</Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Link to="/contacto" className="nav-link">Contacto</Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link href="/sign-in">Login</Nav.Link>
                            </Nav.Item>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>
        );
    }
}
export default NavBar;
