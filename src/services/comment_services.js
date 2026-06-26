import axios from 'axios';

export const fetchComments = () => {
  return new Promise((resolve, reject) => {
    axios.get('/api/comments', {
      params: {},
      headers:{
        'Content-Type': 'application/json',
      }
    }).then(function (response) {
      resolve(response);
    }).catch(function (error) {
      if(error.response.status == 404){
        console.error('Miembro no encontrado')
      }else{
        console.error(error.response.data);
      }
      reject(error.response);
    })
    .then(function () {
      // todo?
    });
  });
}
