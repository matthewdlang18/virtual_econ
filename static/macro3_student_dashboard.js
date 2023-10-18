document.addEventListener("DOMContentLoaded", function() {
    // Initialize variables
    let portfolio = {};
    let assetPrices = {};

    // Fetch initial game state and portfolio
    fetch("/game_state").then(response => response.json()).then(data => {
        // Update portfolio and other game state info
        updatePortfolio(data.portfolio);
        updateAssetPrices(data.current_asset_prices);
    });

    // Event listeners
    const buyButton = document.getElementById("buyButton");
    const sellButton = document.getElementById("sellButton");
    const assetSelect = document.getElementById("asset");
    const quantityInput = document.getElementById("quantity");

    buyButton.addEventListener("click", function() {
        makeTransaction("buy");
    });

    sellButton.addEventListener("click", function() {
        makeTransaction("sell");
    });

    // Function to update portfolio display
    function updatePortfolio(newPortfolio) {
        portfolio = newPortfolio;
        document.getElementById("cash").innerText = portfolio.cash;
        document.getElementById("snp500").innerText = portfolio["S&P500"];
        // Update other asset spans here
    }

    // Function to update asset prices
    function updateAssetPrices(newAssetPrices) {
        assetPrices = newAssetPrices;
        // Populate the asset dropdown
        for (const [asset, price] of Object.entries(assetPrices)) {
            const option = document.createElement("option");
            option.text = asset;
            option.value = asset;
            assetSelect.add(option);
        }
    }

    // Function to make a transaction
    function makeTransaction(type) {
        const asset = assetSelect.value;
        const quantity = Number(quantityInput.value);
        if (!asset || quantity <= 0) {
            alert("Please select a valid asset and quantity.");
            return;
        }

        // Make the API call to perform the transaction
        fetch("/make_transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "asset_name": asset,
                "asset_quantity": quantity,
                "transaction_type": type
            })
        }).then(response => response.json()).then(data => {
            if (data.message === "Transaction successful") {
                // Update the portfolio display
                updatePortfolio(data.portfolio);
            } else {
                alert(data.message);
            }
        });
    }
});
