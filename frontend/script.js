document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed"); // Debugging line

    const newGameButton = document.getElementById('newGame');
    const loadGameButton = document.getElementById('loadGame');

    if (newGameButton) {
        newGameButton.addEventListener('click', function() {
            console.log("New Game button clicked!"); // Debugging line
            // Logic to start a new game goes here
            window.location.href = 'character_creation.html'; // Redirect to character creation page
        });
    } else {
        console.error("New Game button not found!"); // Debugging line
    }

    if (loadGameButton) {
        loadGameButton.addEventListener('click', function() {
            console.log("Load Game button clicked!"); // Debugging line
            // Logic to load a game goes here
            fetch('http://127.0.0.1:5000/api/players') // Fetch saved players
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load saved games');
                }
                return response.json();
            })
            .then(players => {
                console.log("Players loaded:", players); // Debugging line
                // Display saved games to the user
                // Additional logic for displaying saved games can be added here
            })
            .catch(error => {
                console.error('Error loading game data:', error);
                alert('Error loading game data. Please try again.');
            });
        });
    } else {
        console.error("Load Game button not found!"); // Debugging line
    }
});