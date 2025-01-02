document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed for character creation."); // Debugging line

    const characterForm = document.getElementById('characterForm');
    if (characterForm) {
        characterForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the default form submission

            console.log("Character creation form submitted!"); // Debugging line

            const name = document.getElementById('name').value;
            const race = document.getElementById('race').value;
            const classType = document.getElementById('class_type').value;
            const strength = document.getElementById('strength').value;
            const intelligence = document.getElementById('intelligence').value;
            const charisma = document.getElementById('charisma').value;
            const stealth = document.getElementById('stealth').value;
            const dexterity = document.getElementById('dexterity').value;

            // Send the data to the backend
            fetch('http://127.0.0.1:5000/api/players', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    race: race,
                    class_type: classType,
                    strength: strength,
                    intelligence: intelligence,
                    charisma: charisma,
                    stealth: stealth,
                    dexterity: dexterity
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Player created:', data);
                window.location.href = 'main_gameplay.html'; // Redirect to game dashboard after character creation
            })
            .catch(error => {
                console.error('Error creating player:', error);
            });
        });
    } else {
        console.error("Character form not found!");
    }
});
