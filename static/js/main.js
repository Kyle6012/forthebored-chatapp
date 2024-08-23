document.addEventListener('DOMContentLoaded', function() {
    const socket = io.connect(window.location.origin);

    const sendButton = document.getElementById('send');
    const messageBox = document.getElementById('message');
    const chatBox = document.getElementById('chat-box');
    const sendPrivateButton = document.getElementById('send-private');
    const privateMessageBox = document.getElementById('private-message');
    const receiverInput = document.getElementById('receiver');

    let room = 'public';
    let username = prompt('Enter your username:');

    socket.emit('join', { 'username': username, 'room': room });

    sendButton.onclick = function() {
        const message = messageBox.value;
        if (message) {
            socket.emit('message', { 'msg': message, 'username': username, 'room': room });
            messageBox.value = '';
        }
    };

    sendPrivateButton.onclick = function() {
        const privateMessage = privateMessageBox.value;
        const receiver = receiverInput.value;
        if (privateMessage && receiver) {
            socket.emit('private_message', { 'msg': privateMessage, 'receiver': receiver });
            privateMessageBox.value = '';
        }
    };

    socket.on('message', function(data) {
        const msg = document.createElement('p');
        msg.textContent = `${data.username}: ${data.msg}`;
        chatBox.appendChild(msg);
    });

    socket.on('private_message', function(data) {
        const msg = document.createElement('p');
        msg.textContent = `Private from ${data.sender}: ${data.msg}`;
        chatBox.appendChild(msg);
    });

    socket.on('status', function(data) {
        const msg = document.createElement('p');
        msg.textContent = data.msg;
        chatBox.appendChild(msg);
    });
});
