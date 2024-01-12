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
      appendMessage(data, 'bot');
      document.getElementById('user-input').value = ''; // Clear the input after sending
    })
    .catch(error => console.error('Error:', error));
}

function requestReviewSummary(place_id) {
  // Make sure to handle the case where place_id is not defined
  if (!place_id) {
    console.error('No place_id provided for review summary.');
    return;
  }

  // Call the backend to get the review summary for the given place_id
  fetch(`/review_summary?place_id=${place_id}`)
    .then(response => response.json())
    .then(data => {
      // Append the review summary to the chat
      appendMessage(data, 'bot');
    })
    .catch(error => {
      console.error('Error fetching review summary:', error);
    });
}



function appendMessage(message, sender) {
  const chatBox = document.getElementById('chat-box');
  const messageElement = document.createElement('div');
  messageElement.className = `message ${sender}`;
  
  const contentElement = document.createElement('div');
  contentElement.className = 'content';
  //contentElement.textContent = message;
  if (sender === 'user') {
  contentElement.textContent = message;
  messageElement.appendChild(contentElement);
  chatBox.appendChild(messageElement);
  }

  if (sender === 'bot') {
    contentElement.innerHTML = message.message;
    const imgElement = document.createElement('img');
    imgElement.src = 'static/chatbot.png';
    imgElement.alt = 'Chatbot';
    messageElement.appendChild(imgElement);
    messageElement.appendChild(contentElement);
    chatBox.appendChild(messageElement);
    // Conditionally append the review summary button
    if (message.showReviewButton) {
      const buttonElement = document.createElement('button');
      buttonElement.className = 'review-summary-button';
      buttonElement.textContent = 'Review Summary';
      buttonElement.onclick = (function(place_id) {
        return function() { requestReviewSummary(place_id); };
      })(message.place_id);
      chatBox.appendChild(buttonElement);
    }
  }

  // Scroll to the bottom of the chat box
  chatBox.scrollTop = chatBox.scrollHeight;
}
