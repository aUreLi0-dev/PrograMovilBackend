import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import Footer from '../widgets/Footer.jsx'
import NavBar from '../widgets/NavBar.jsx';
import ContactPage from '../pages/ContactPage.jsx';
import AboutUsPage from '../pages/AboutUsPage.jsx';

const Web = () => {
  return (
    <Router>
      {/* Navbar */}
      <NavBar/>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/contacto" element={<ContactPage />} />
        <Route path="/nosotros" element={<AboutUsPage />} />
      </Routes>
      <Footer/>
    </Router>
  );

  return (
    <>
      

      
    </>
  );
};

export default Web;
