import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { Amplify } from 'aws-amplify'
import config from './aws-exports.js'

// Function to handle form submission
function handleFormSubmission(event) {
  event.preventDefault(); // Prevent the default form submission

  // Get the form data
  var formData = new FormData(event.target);

  // Make an AJAX request to the server to register the user
  fetch('/register', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    // Handle the response from the server
    if (data.success) {
      // Registration successful, redirect to the dashboard or desired page
      window.location.href = '/dashboard';
    } else {
      // Registration failed, display the error message to the user
      var errorElement = document.getElementById('error-message');
      errorElement.textContent = data.message;
      errorElement.style.display = 'block';
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

// Add event listener to the form submit event
var registerForm2 = document.getElementById('register-form');
registerForm2.addEventListener('submit', handleFormSubmission);



