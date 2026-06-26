import React, { Component } from 'react';
import { Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import './DataTable.css'

class DataTable extends Component {
  // Array comments = [];
  constructor(props) {
    super(props);
    this.state = { 
      data: [],
      deleted: [],
      edited: [],
      created: [],
    };
  }
  // Método del ciclo de vida que se ejecuta después de que el componente se monta
  componentDidMount() {
    this.fetchData();
  }

  postChanges = () => {
    const { postUrl } = this.props;
    const { created, edited, deleted, } = this.state;

    fetch(postUrl, {
      method: 'POST', // Método HTTP
      headers: {
          'Content-Type': 'application/json' // Indicar que se envía JSON
        },
        body: JSON.stringify({
          created: created, 
          edited: edited, 
          deleted: deleted,
        }) // Convertir el objeto a JSON
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error en la solicitud: ${response.status}`);
        }
        return response.json(); // Convertir la respuesta en JSON
      })
      .then(data => {
        alert('Cambios realizados en la DB');
        this.setState({
          created: [],
          edited: [],
          deleted: [],
        });
      })
      .catch(error => {
        alert('Cambios realizados en la DB');
        console.error('Error:', error);
      });
  }

  fetchData = () => {
    const { fetchUrl, columns } = this.props;
    const token = localStorage.getItem('jwtToken');
    fetch(fetchUrl,{
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`
    }}).then(response => {
        if (!response.ok) {
          throw new Error('Error en la solicitud: ' + response.status);
        }
        return response.json(); // Convertir la respuesta a JSON
      })
      .then(data => {
        this.setState({
          data: data
        })
      })
      .catch(error => {
        console.error('Error:', error); // Manejo de errores
      });
  }

  deleteRow = (idToRemove, key) => {
    const { data, deleted } = this.state;
    this.setState({
      data: data.filter(item => item[key] !== idToRemove),
      deleted: [...deleted, idToRemove]
    }) 
  }

  renderButtons = (column, item) => {
    return column.buttons.map((button, index) => (
      button.action === 'link' ? (
        <Link to={`${button.url}${item[button.key]}`}>
          <Button variant="info">{button.label}</Button>
        </Link>
      ) : button.action == 'delete'  ? (
        <Button variant="danger" onClick={() => this.deleteRow(item[button.key], button.key)}>{button.label}</Button>
      ) : (
        <button key={index} onClick={() => console.log(item)}>
          {button.label}
        </button>
      )
    ));
  };
  

  renderCellContent = (column, item) => {
    switch (column.type) {
      case 'td':
        return item[column.key];
      case 'buttons':
        return this.renderButtons(column, item);
      default:
        return null;
    }
  };  

  render() {
    const { columns } = this.props;
    const { data } = this.state;
    return (
      <table class="table table-striped table-bordered table-hover">
          <thead class="table-dark">
            <tr>
            {columns.map((column) => ( 
              <th style={column.styles}>{column.label}</th>  
            ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, rowIndex) => (
              <tr key={rowIndex}>
                {columns.map((column, colIndex) => (
                  <td key={colIndex} style={column.styles}>
                    {this.renderCellContent(column, item)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
    );
  }
}

export default DataTable;