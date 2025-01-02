document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed for game dashboard."); // Debugging line

    const startAdventureButton = document.getElementById('startAdventure');
    if (startAdventureButton) {
        startAdventureButton.addEventListener('click', function() {
            console.log("Start Adventure button clicked!"); // Debugging line
            // Logic to start the adventure goes here
            // For example, redirecting to a game scene or initiating game logic
            window.location.href = 'game_scene.html'; // Redirect to the game scene page
        });
    } else {
        console.error("Start Adventure button not found!"); // Debugging line
    }
});
