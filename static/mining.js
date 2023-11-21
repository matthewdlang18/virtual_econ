document.addEventListener('DOMContentLoaded', function() {
    const manualSubmitButton = document.getElementById('manual_submit');
    const autoMineButton = document.getElementById('auto_mine');
    const miningResultDiv = document.getElementById('mining_result');
    const transactionInput = document.getElementById('transaction');
    const nonceInput = document.getElementById('nonce');
    const currentLevelSpan = document.getElementById('current_level');

    // Placeholder for student_id and class, which would be fetched or passed from your existing system
    const studentId = '{{ student_id }}';
    const studentClass = '{{ student_class }}';

    manualSubmitButton.addEventListener('click', function() {
        const transaction = transactionInput.value;
        const nonce = nonceInput.value;
        const level = parseInt(currentLevelSpan.textContent);

        fetch('/hash', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: studentId,
                class: studentClass,
                transaction: transaction,
                nonce: nonce,
                level: level
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                miningResultDiv.innerHTML = `<span style="color:green">${data.message}</span><br>Hash: ${data.hash}`;
            } else {
                miningResultDiv.innerHTML = `<span style="color:red">${data.message}</span><br>Hash: ${data.hash}`;
            }
        });
    });

    autoMineButton.addEventListener('click', function() {
        const transaction = transactionInput.value;
        const level = parseInt(currentLevelSpan.textContent);

        fetch('/autohash', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: studentId,
                class: studentClass,
                transaction: transaction,
                level: level
            })
        })
        .then(response => response.json())
        .then(data => {
            nonceInput.value = data.nonce;
            if (data.success) {
                miningResultDiv.innerHTML = `<span style="color:green">${data.message}</span><br>Hash: ${data.hash}`;
            } else {
                miningResultDiv.innerHTML = `<span style="color:red">${data.message}</span><br>Hash: ${data.hash}`;
            }
        });
    });
});
