// Add this JavaScript in static/scripts.js

function sendMessage() {
  var userInput = document.getElementById('user-input').value;
  if (userInput.trim() === '') return; // Prevent sending empty messages

  // Append user message to the chat
  appendMessage(userInput, 'user');

  // Send the message to the Flask backend
  fetch(`/get?msg=${encodeURIComponent(userInput)}`)
    .then(response => response.json())
    .then(data => {
      // Append the bot response to the chat
      appendMessage(data.message, 'bot');
      document.getElementById('user-input').value = ''; // Clear the input after sending
    })
    .catch(error => console.error('Error:', error));
}

function appendMessage(message, sender) {
  const chatBox = document.getElementById('chat-box');
  const messageElement = document.createElement('div');
  messageElement.className = `message ${sender}`;
  
  const contentElement = document.createElement('div');
  contentElement.className = 'content';
  contentElement.textContent = message;

  if (sender === 'bot') {
    const imgElement = document.createElement('img');
    imgElement.src = 'static/chatbot.png';
    imgElement.alt = 'Chatbot';
    messageElement.appendChild(imgElement);
  }
  
  messageElement.appendChild(contentElement);
  chatBox.appendChild(messageElement);

  // Scroll to the bottom of the chat box
  chatBox.scrollTop = chatBox.scrollHeight;
}
