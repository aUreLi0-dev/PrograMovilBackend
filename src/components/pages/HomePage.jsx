import React, { Component } from 'react';
import { Carousel, Container, Row, Col, Card } from 'react-bootstrap';
import Comment from '../widgets/Comment.jsx';
import './HomePage.css'

class HomePage extends Component {
  // Array comments = [];
  constructor(props) {
    super(props);
    // Estado inicial del componente
    this.state = {
      comments: [],
    };
  }
  // Método del ciclo de vida que se ejecuta después de que el componente se monta
  componentDidMount() {
    console.log('Componente montado');
    document.title = 'Bienvenido';
    fetch('/api/comments',{
      method: 'GET',
      headers: {}}
    ).then(response => {
        if (!response.ok) {
          throw new Error('Error en la solicitud: ' + response.status);
        }
        return response.json(); // Convertir la respuesta a JSON
      })
      .then(data => {
        console.log('Datos:', data); // Procesar los datos
        //this.setComments(data);
        this.setState({
          comments: data,
        });
      })
      .catch(error => {
        console.error('Error:', error); // Manejo de errores
      });
  }
  // Método del ciclo de vida que se ejecuta justo antes de que el componente se desmonte
  componentWillUnmount() {
    console.log('Componente a punto de desmontarse');
  }
  render() {
    const { comments } = this.state;

    return (
      <>
      {/* Carousel */}
      <Carousel id="carouselExample" ride="carousel">
        {/* Indicadores */}
        <Carousel indicators>
          <Carousel.Item>
            <img src="/img/img01.jpeg" className="d-block w-100" alt="Imagen 1" />
            <Carousel.Caption>
              <h5>Imagen 1</h5>
              <p>Descripción breve de la primera imagen.</p>
            </Carousel.Caption>
          </Carousel.Item>
          <Carousel.Item>
            <img src="/img/img02.jpeg" className="d-block w-100" alt="Imagen 2" />
            <Carousel.Caption>
              <h5>Imagen 2</h5>
              <p>Descripción breve de la segunda imagen.</p>
            </Carousel.Caption>
          </Carousel.Item>
          <Carousel.Item>
            <img src="/img/img03.jpeg" className="d-block w-100" alt="Imagen 3" />
            <Carousel.Caption>
              <h5>Imagen 3</h5>
              <p>Descripción breve de la tercera imagen.</p>
            </Carousel.Caption>
          </Carousel.Item>
        </Carousel>
      </Carousel>

      {/* Info Section */}
      <Container className="my-5">
        <Row className="align-items-center">
          {/* Columna Izquierda */}
          <Col md={6}>
            <h1 className="display-5" id="titulo">Título de la Sección</h1>
            <p className="lead">
              Este es un texto de ejemplo que puedes personalizar. Aquí puedes describir algo importante o destacar información relevante.
            </p>
            <p>
              Bootstrap facilita la creación de diseños responsivos y atractivos para que tu contenido se vea bien en cualquier dispositivo.
            </p>
          </Col>

          {/* Columna Derecha */}
          <Col md={6}>
            <img 
              id="figurita" 
              src="/img/img01.jpeg" 
              alt="Imagen de ejemplo" 
              height="500" 
              width="300" 
              className="img-fluid rounded" 
            />
          </Col>
        </Row>
      </Container>

      {/* Atractivos Turísticos */}
      <Container className="my-5">
        <Row className="g-4" id="fila">
          {/* Atractivo 1 */}
          <Col md={4}>
            <Card className="h-100">
              <Card.Img variant="top" src="/img/img01.jpeg" alt="Lugar emblemático" />
              <Card.Body>
                <Card.Title>Nombre del Lugar Emblemático</Card.Title>
                <Card.Text>
                  Este lugar es el corazón cultural de Végueta. Su arquitectura histórica y su ambiente único lo convierten en una visita obligada.
                </Card.Text>
              </Card.Body>
              <Card.Footer>
                <small className="text-muted">📍 Ubicación: Centro Histórico</small>
              </Card.Footer>
            </Card>
          </Col>

          {/* Atractivo 2 */}
          <Col md={4}>
            <Card className="h-100">
              <Card.Img variant="top" src="/img/img02.jpeg" alt="Parque o espacio natural" />
              <Card.Body>
                <Card.Title>Parque o Espacio Natural</Card.Title>
                <Card.Text>
                  Un oasis en medio de la ciudad. Perfecto para relajarse, caminar entre la naturaleza o disfrutar de un picnic.
                </Card.Text>
              </Card.Body>
              <Card.Footer>
                <small className="text-muted">🌳 Actividades: Senderismo, fotografía, picnics</small>
              </Card.Footer>
            </Card>
          </Col>

          {/* Atractivo 3 */}
          <Col md={4}>
            <Card className="h-100">
              <Card.Img variant="top" src="/img/img03.jpeg" alt="Museo o centro cultural" />
              <Card.Body>
                <Card.Title>Museo o Centro Cultural</Card.Title>
                <Card.Text>
                  Descubre la historia y el arte de la ciudad en este emblemático museo. Exhibiciones permanentes y temporales para todos los gustos.
                </Card.Text>
              </Card.Body>
              <Card.Footer>
                <small className="text-muted">🎨 Horarios: 10:00 AM - 6:00 PM</small>
              </Card.Footer>
            </Card>
          </Col>
        </Row>
        <Row className="g-4">
          <h1 className="display-5" id="titulo">Comentarios</h1>
          {comments.map((comment, index) => (
            <Col md={4}>
              <Comment 
                guest={comment.guest} 
                comment={comment.comment}
                date={comment.date} />
            </Col>
          ))}
        </Row>
      </Container>
    </>
    );
  }
}

export default HomePage;