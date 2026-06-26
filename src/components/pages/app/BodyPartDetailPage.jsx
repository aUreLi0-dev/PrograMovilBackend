import React from "react";
import { useParams } from "react-router-dom";
import "./BodyPartDetailPage.css";

const BodyPartDetailPage = () => {
  const { id } = useParams(); // Obtiene el ID de la URL

  return (
    <div className="container my-5 contacto-container">
      <h1>Detalle de Parte del Cuerpo</h1>
      {id ? (
        <p>Mostrando detalles de la parte del cuerpo con ID: {id}</p>
      ) : (
        <p>No se proporcionó ID</p>
      )}
    </div>
  );
};

export default BodyPartDetailPage;
