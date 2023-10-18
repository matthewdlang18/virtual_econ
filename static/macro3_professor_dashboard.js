document.addEventListener('DOMContentLoaded', (event) => {
  // Start Game button
  const startGameBtn = document.getElementById("startGameBtn");
  startGameBtn.addEventListener("click", function() {
    fetch('/initialize_game', {
      method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
    });
  });

  // New Round button
  const newRoundBtn = document.getElementById("newRoundBtn");
  newRoundBtn.addEventListener("click", function() {
    fetch('/new_round', {
      method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      alert(`New round: ${data.new_round_number}`);
    });
  });

  // Lock Game button
  const lockGameBtn = document.getElementById("lockGameBtn");
  lockGameBtn.addEventListener("click", function() {
    fetch('/lock_game', {
      method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
    });
  });

  // Unlock Game button
  const unlockGameBtn = document.getElementById("unlockGameBtn");
  unlockGameBtn.addEventListener("click", function() {
    fetch('/unlock_game', {
      method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
    });
  });
});
