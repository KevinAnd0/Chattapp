function currDate() {
  let date = new Date();
  let year = date.getFullYear();
  let day = date.getDate();
  let month = date.getMonth() + 1;

  if (day < 10) day = "0" + day;
  if (month < 10) month = "0" + month;

  let cur_day = day + "-" + month + "-" + year;

  let hours = date.getHours();
  let minutes = date.getMinutes();
  let seconds = date.getSeconds();

  if (hours < 10) hours = "0" + hours;
  if (minutes < 10) minutes = "0" + minutes;
  if (seconds < 10) seconds = "0" + seconds;

  return cur_day + " " + hours + ":" + minutes;
}


async function getUser() {
  let res = await fetch('/get_username')
  let result = await res.json();
  return result['name']
}


async function searchUser (search) {
  let res = null
  if (search){
    res = await fetch('/search_users/' + search)
  }
  else{
    res = await fetch('/search_users')
  }
  return await res.json()
}


async function getFriends(username) {
  let res = await fetch('/get_friends/' + username)
  return await res.json()
}


function changeStatus(item) {
  if (item.online === 1) {
    return { username: item.username, online: 'Online'};
  }
  else {
    return { username: item.username, online: 'Offline'};
  }
}


async function getMessages(data) {
  let res = await fetch('/get_messages_one_user', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
    })
  return await res.json()
}


async function renderUsers(result) {
  let list = ''
  if (result === undefined) {
    let username = await getUser()
    result = await getFriends(username)
    list = result.map(changeStatus)

    $('#friends').empty()
    list.forEach(function (user) {
      $('#friends').append(`
      <div class="friendcontainer">     
      <b style="color:#000" class="right" id='friendName'>${user.username}</b>
      <span class="time-right">${user.online}</span>
      </div>
      <hr>
      `)
    })
  }
  else {
    list = result.map(changeStatus)
    $('#friends').empty()
    list.forEach(function (user) {
      $('#friends').append(`
      <div class="friendcontainer">     
      <b style="color:#000" class="right">
      <button class="btn btn-success" type="submit" id="addBtn">${user.username}</button>
      </b>
      <span class="time-right">${user.online}</span>
      </div>
      <hr>
      `)
    })
  }
}


function renderMsg(msg) {
    $('#messages').append(`
    <div class="messageContainer"> 
    <b style="color:#000" class="right">${msg.sender}</b>
    <p>${msg.message}</p>
    <span class="time-right">${msg.time}</span>
    </div>
    <hr>
    `)
}


async function addFriend(data) {
  let res = await fetch('/add_friend', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return await res.json()
}


function scrollToBottom() {
  $('#messages').animate({
    scrollTop: $('#messages').get(0).scrollHeight
  }, 1500);
}


// renders friends if search val is empty, otherwise renders searched user
$('#friendsForm').on('submit', async function(e) {
  e.preventDefault()
  let search = $('#searchFriend').val()
  if (search !== '') {
    result = await searchUser(search)
    await renderUsers(result)
  }
  else {
    await renderUsers()
  }
  $('#searchFriend').val('')
})


// adds selected user to friends list and renders new friendslist with added friend
$('body').on('click', '#addBtn', async function() {
  data = {
    sender: await getUser(),
    receiver: $(this).text()
  }
  await addFriend(data)
  await renderUsers()
})


// retreives message history for selected user on friendslist
$('body').on('click', '.friendcontainer', async function(e) {
  data = {
    user1: await getUser(),
    user2: $('b').text()
  }
  let result = await getMessages(data)
  $('#messages').empty()
  result.forEach(renderMsg)
  scrollToBottom()
})


$('#messageForm').on('change', '.inputImage', async  function () {
  // console.log('check')
  // let check = document.querySelector(".inputImage").files;

  // let check = $(this).files
//   const reader = new FileReader();
//   reader.onload = function() {
//     const base64 = this.result.replace(/.*base64,/, '');
//     socket.emit('image', base64);
//   };
//   reader.readAsDataURL(this.files[0]);

// });

const reader = new FileReader();
reader.onload = function() {
  const bytes = new Uint8Array(this.result);
  socket.emit('image', bytes);
};
reader.readAsArrayBuffer(this.files[0]);

});


const socket = io.connect('http://' + document.domain + ':' + location.port, {'forceNew':true });
socket.on('connect', async function() {
  const username = await getUser()
  await renderUsers()

  socket.emit('connecting', {
    user: username,
    socket_id: socket.id
  })

  let form = $('#messageForm').on('submit',async (e) => {
    let input = $('#friendName').text()
    let message = $('#inputMessage').val()
    e.preventDefault()
    if (message !== '') {
      data = {
        sender: username, 
        user2: input, 
        message: message,
        time: currDate()
      }
      socket.emit('message', data)
      renderMsg(data)
      scrollToBottom()
    }  
    $('#inputMessage').val( '' ).focus()
  })
})


socket.on('response', function (msg) {
  if(typeof msg.sender !== 'undefined') {
    renderMsg(msg)
  }
})

socket.on('receive image', async function (image) {
  const img = new Image();
  img.src = `data:image/png;base64,${image.data}`; 
  $('#messages').append(`
    <br><img id="view-note-image" src="${img}"></img>
  `)
})