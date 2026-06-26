export const validateEmail = (email) => {
  // Expresión regular para validar el formato de un email electrónico
  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  // Verificamos si el email cumple con la expresión regular
  return regex.test(email);
}

