import React, { Component } from 'react';
import { Carousel, Container, Row, Col, Card } from 'react-bootstrap';
import './Comment.css'

class Comment extends Component {
  // Array comments = [];
  constructor(props) {
    super(props);
  }
  // Método del ciclo de vida que se ejecuta después de que el componente se monta
  componentDidMount() {
  }

  render() {
    const { comment, guest, date } = this.props;
    return (
      <Card>
        <Card.Body>
          <Card.Title>{guest}</Card.Title>
          <Card.Subtitle className="mb-2 text-muted">{date}</Card.Subtitle>
          <Card.Text>{comment}</Card.Text>
        </Card.Body>
      </Card>
    );
  }
}

export default Comment;