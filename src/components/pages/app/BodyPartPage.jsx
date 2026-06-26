import React, { Component } from 'react';
import { Link } from "react-router-dom";
import { Button } from "react-bootstrap";
import './BodyPartPage.css'
import DataTable from '../../widgets/DataTable';

class BodyPartPage extends Component {
  // Array comments = [];
  constructor(props) {
    super(props);
    this.dataTable = React.createRef(); 
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
        <h1>Listado de Partes del Cuerpo</h1>
        <Link to="/body-parts/add">
          <Button variant="success">Crear</Button>
        </Link>
        <Button variant="primary" onClick={() => this.dataTable.current.postChanges()}>
          Guardar Cambios
        </Button>
        <DataTable 
          ref={this.dataTable} 
          fetchUrl='/admin/apis/body-parts'
          postUrl='/admin/apis/body-parts/many'
          columns={[
            {
              type: 'td', 
              label: 'id', 
              key: 'id', 
              styles: {display: 'none'}
            },
            {
              type: 'td', 
              label: 'Nombre', 
              key: 'name', 
              styles: {}
            },
            {
              type: 'buttons', 
              label: 'Operaciones', 
              key: 'id', 
              styles: {}, 
              buttons: [
                {
                  label: 'Editar',
                  action: 'link',
                  url: '/body-parts/',
                  key: 'id'
                },
                {
                  label: 'Eliminar',
                  action: 'delete',
                  url: '/apis/body-parts/',
                  key: 'id'
                }
              ]
            }
          ]}
        />
      </div>
    );
  }
}

export default BodyPartPage;