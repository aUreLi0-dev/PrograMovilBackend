import React, { Component } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import './InputText.css';

class InputText extends Component {
  constructor(props) {
    super(props);
    // Estado inicial del componente
    this.state = { 
      type: props.type || 'text',
      id: props.id || Math.random().toString(36).substring(2, 12),
      value: props.value || '',
      valid: null,
      feedback: '',
    };
  }

  static defaultProps = {
    onChangeValidations: [],
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
    const { value } = this.state;
    const regex = /^[a-zA-Z0-9._%+-]+@certus\.edu\.pe$/;
    if(value != ''){
      return regex.test(value);
    }else{
      return null;
    }
  }

  validateMessage = () => {
    const { message } = this.state;
    //console.log(message)
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
      {value: e.target.value} // e.targe.value: es el valor actual de input
    , () => {
      const { onChangeValidations } = this.props;
      var isValid = true;
      var feedback = '';
      onChangeValidations.forEach((validation) => {
        if(isValid){
          if(validation.type == 'email'){
            isValid = this.validateEmail();
          }else if(validation.type == 'maxLength'){
            isValid = e.target.value.length == 0 ? null : (e.target.value.length <= validation.max ? true : false);
          }else if(validation.type == 'dni'){
            isValid = null;
            // TODO
          }else if(validation.type == 'custom'){
            console.log('custom')
            validation.def();
          }else{
            console.error(`validación ${validation.type} no existe`);
            isValid = null;
          }
          // update feedback
          if(isValid){
            feedback = validation.validText;
          }else if(feedback == null){
            feedback = '';
          }else{
            feedback = validation.invalidText;
          }
        }
      });
      this.setState({valid: isValid});
      this.setState({feedback: feedback});
      // Enviar la información de validación al componente padre
      if (this.props.onValidationChange) {
        this.props.onValidationChange(isValid);
      }
    });
  }

  render() {
    const { label, placeholder, name } = this.props;
    const { type, id, value, valid, feedback } = this.state;
    return (
      <Form.Group className="mb-6" controlId={id}>
        <Form.Label>{label}</Form.Label>
        <Form.Control 
          type={type} 
          placeholder={placeholder}
          value={value}
          name={name}
          onChange={this.handleChange}
          className={valid == null ? '': (valid ? 'is-valid': 'is-invalid')}
          required />
        {valid == null ? '' :
        valid == true ?
          <Form.Control.Feedback>
            {feedback}
          </Form.Control.Feedback>
        : <Form.Control.Feedback type="invalid">  
          {feedback}
        </Form.Control.Feedback>}
      </Form.Group>
    );
  }
}
export default InputText;