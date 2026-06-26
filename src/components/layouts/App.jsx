import React from 'react';
import { Navbar, Nav, Container, Row, Col } from 'react-bootstrap';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from '../pages/app/HomePage';
import BodyPartPage from '../pages/app/BodyPartPage';
import BodyPartDetailPage from '../pages/app/BodyPartDetailPage';

const App = () => {
  return (
    <Router basename="/admin">
      {/* navbar */}
      <Navbar bg="dark" variant="dark" expand="lg" fixed="top">
        <Container>
          <Navbar.Brand as={Link} to="/admin">Admin </Navbar.Brand>
          <Navbar.Toggle aria-controls="navbarNav" />
          <Navbar.Collapse id="navbarNav">
            <Nav className="ms-auto">
              <Nav.Item>
                <Nav.Link as={Link} to="">Home</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link as={Link} to="/body-parts">Partes del Cuerpo</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link as={Link} to="/users">Usuarios</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link as={Link} to="/clientes">Clientes</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link as={Link} to="/sign-out" id="btnSignOut">Salir</Nav.Link>
              </Nav.Item>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      {/* partial */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/body-parts" element={<BodyPartPage />} />
        <Route path="/body-parts/:id" element={<BodyPartDetailPage />} />
      </Routes>
    </Router>
    
  );
};

export default App;
