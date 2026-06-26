function crearTarjetas(){
  var contenidos = [{
    'src': '/img/img02.jpeg',
    'alt': 'Parque o espacio natural',
    'title': 'Parque o Espacio Natural',
    'p': 'Un oasis en medio de la ciudad. Perfecto para relajarse, caminar entre la naturaleza o disfrutar de un picnic con vistas espectaculares.',
    'footer': '🌳 Actividades: Senderismo, fotografía, picnics',
  },{
    'src': '/img/img03.jpeg',
    'alt': 'Museo o centro cultural',
    'title': 'Museo o centro cultural',
    'p': 'Descubre la historia y el arte de la ciudad en este emblemático museo. Exhibiciones permanentes y temporales para todos los gustos.',
    'footer': '🎨 Horarios: 10:00 AM - 6:00 PM',
  }];

  contenidos.forEach(function(contenido) {
    var div1 = document.createElement('div');
    div1.classList.add('col-md-4');
    var div2 = document.createElement('div');
    div2.classList.add('card');
    div2.classList.add('h-100');
    var imagen = document.createElement('img');
    imagen.src = contenido.src;
    imagen.classList.add('card-img-top');
    imagen.alt = contenido.alt;
    var cardBody = document.createElement('div');
    cardBody.classList.add('card-body');
    var h5 = document.createElement('h5');
    h5.classList.add('card-title');
    h5.innerHTML = contenido.title;
    var p = document.createElement('p');
    p.classList.add('card-text');
    p.innerHTML = contenido.p;
    cardBody.appendChild(h5);
    cardBody.appendChild(p);
    var cardFooter = document.createElement('div');
    cardFooter.classList.add('card-footer');
    var small = document.createElement('small');
    small.classList.add('text-muted');
    small.innerHTML = contenido.footer;
    cardFooter.appendChild(small);
  
    div2.appendChild(imagen)
    div2.appendChild(cardBody)
    div2.appendChild(cardFooter)
    div1.appendChild(div2)
  
    var fila = document.getElementById('fila');
    fila.appendChild(div1);
  });
}

document.getElementById("email").addEventListener("blur", function() {
  const regexCorreo = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  var correo = this.value;
  if (regexCorreo.test(correo) == false) {
    alert(`${correo} NO es un correo válido.`);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  console.log('hola home');
  var htitulo = document.getElementById('titulo');
  console.log(htitulo);
  htitulo.innerHTML = 'hola desde Végueta';
  htitulo.classList.add('text-danger-emphasis');
  console.log(htitulo.classList);
  crearTarjetas();
});

document.getElementById("figurita").addEventListener("mouseover", function() {
  var figurita = document.getElementById('figurita');
  figurita.src = '/img/img02.jpeg';
});

document.getElementById("figurita").addEventListener("mouseout", function() {
  var figurita = document.getElementById('figurita');
  figurita.src = '/img/img01.jpeg';
});

