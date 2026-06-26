const showUseToEdit = (user) => {
  console.log(user);
  document.getElementById('txtId').value = user.id;
  document.getElementById('txtMemberId').value = user.member_id;
  document.getElementById('txtUserName').value = user.user_name;
  document.getElementById('txtPassword').value = user.password;
  modalBootstrap.show();
}

const deleteUser = (id) => {
  alert(id);

  // Corrección del paréntesis de cierre
  fetch(`/api/admin/users/${id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  }) // ← Paréntesis de cierre correcto aquí
  .then(response => {
    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.status}`);
    }
    return response.json(); // Convertir la respuesta en JSON
  })
  .then(data => {
    console.log('Usuario eliminado:', data);
    alert('Usuario eliminado correctamente.');
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Hubo un error al eliminar el usuario.');
  });
};


const getUsers = () => {
  const token = localStorage.getItem('jwtToken');
  fetch('/api/admin/users',{
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
      var tbody = document.getElementById('users');
      data.forEach((user) => {
        var tr = document.createElement('tr');
        var tdUserName = document.createElement('td');
        tdUserName.innerHTML = user.user_name;
        var tdPassword = document.createElement('td');
        tdPassword.innerHTML = user.password
        var tdActions = document.createElement('td');
        var btnEdit = document.createElement('button');
        btnEdit.classList.add('btn');
        btnEdit.classList.add('btn-primary');
        btnEdit.innerHTML = 'Editar';
        btnEdit.addEventListener('click', () => showUseToEdit(user))
        var btnDelete = document.createElement('button');
        btnDelete.innerHTML = 'Eliminar';
        btnDelete.classList.add('btn');
        btnDelete.classList.add('btn-danger');
        btnDelete.addEventListener('click', () => deleteUser(user.id))
        tdActions.appendChild(btnEdit);
        tdActions.appendChild(btnDelete);
        tr.appendChild(tdUserName);
        tr.appendChild(tdPassword);
        tr.appendChild(tdActions);
        tbody.appendChild(tr);
      });
      console.log('Datos:', data); // Procesar los datos
    })
    .catch(error => {
      console.error('Error:', error); // Manejo de errores
    });
}

window.onload = getUsers;
const modalElement = document.getElementById('miModal');
const modalBootstrap = new bootstrap.Modal(modalElement);

document.getElementById('btnAdd').addEventListener('click', () => {
  modalBootstrap.show();
});

const create = (data) => {
  // Usar fetch para enviar la solicitud POST
  fetch('/api/admin/users', {
   method: 'POST', // Método HTTP
   headers: {
       'Content-Type': 'application/json' // Indicar que se envía JSON
     },
     body: JSON.stringify(data) // Convertir el objeto a JSON
   })
   .then(response => {
     if (!response.ok) {
       throw new Error(`Error en la solicitud: ${response.status}`);
     }
     alert();
     return response.json(); // Convertir la respuesta en JSON
   })
   .then(data => {
     console.log('Respuesta:', data);
   })
   .catch(error => {
     console.error('Error:', error);
   });
 };

const edit = (data) => {
 // Usar fetch para enviar la solicitud POST
 fetch('/api/admin/users', {
  method: 'PUT', // Método HTTP
  headers: {
      'Content-Type': 'application/json' // Indicar que se envía JSON
    },
    body: JSON.stringify(data) // Convertir el objeto a JSON
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.status}`);
    }
    alert();
    return response.json(); // Convertir la respuesta en JSON
  })
  .then(data => {
    console.log('Respuesta:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
};

document.getElementById('btnSave').addEventListener('click', () => {
  var id = document.getElementById('txtId').value;
  var userName = document.getElementById('txtUserName').value;
  var password = document.getElementById('txtPassword').value;
  var memberId = document.getElementById('txtMemberId').value;
  const data = {
    id: id,
    user_name: userName,
    password: password,
    member_id: memberId,
  };
  if(data.id == 'E'){
    create(data);
  }else{
    edit(data);
  }
});