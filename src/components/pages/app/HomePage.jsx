import React, { Component } from 'react';
import './HomePage.css'

class HomePage extends Component {
  // Array comments = [];
  constructor(props) {
    super(props);
  }
  // Método del ciclo de vida que se ejecuta después de que el componente se monta
  componentDidMount() {
  }
  // Método del ciclo de vida que se ejecuta justo antes de que el componente se desmonte
  componentWillUnmount() {
    
  }
  render() {
    return (
      <div class="container my-5 contacto-container">
        <h1>Home</h1>
      </div>
    );
  }
}

export default HomePage;