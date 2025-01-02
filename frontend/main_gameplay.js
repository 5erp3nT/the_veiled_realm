document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed for main gameplay."); // Debugging line

    const sendMessageButton = document.getElementById('sendMessage');
    const playerInput = document.getElementById('playerInput');
    const narratorMessages = document.getElementById('narratorMessages');

    sendMessageButton.addEventListener('click', function() {
        const userMessage = playerInput.value;
        if (userMessage) {
            // Display the player's message in the chat window
            narratorMessages.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;
            playerInput.value = ''; // Clear the input field

            // Send the player's input to the backend for processing
            fetch(process.env.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                // Display the response from the game master
                narratorMessages.innerHTML += `<p><strong>Game Master:</strong> ${data.response}</p>`;
                // Optionally scroll to the bottom of the chat window
                narratorMessages.scrollTop = narratorMessages.scrollHeight;
            })
            .catch(error => {
                console.error('Error processing game action:', error);
            });
        }
    });
});
