import random
import matplotlib.pyplot as plt

# Function to simulate Bitcoin prices and returns for 40 years
def adjust_bitcoin_params(bitcoin_price):
    base_avg_return = 0.50
    base_std_dev = 0.75
    price_threshold = 100000

    # Calculate the number of 100k increments above the threshold
    increments_above_threshold = max(0, (bitcoin_price - price_threshold) // 50000)

    # Adjust average return and standard deviation
    avg_return = max(0.10, base_avg_return - increments_above_threshold * 0.1)
    std_dev = max(0.05, base_std_dev - increments_above_threshold * 0.20)

    return avg_return, std_dev


# Function to simulate Bitcoin prices and returns for 40 years with a four-year cycle
def simulate_bitcoin_price_with_business_cycle():
    years = 40
    rounds_per_year = 1  # One round per year
    simulations = 1000

    final_bitcoin_prices = []

    for _ in range(simulations):
        # Initial Bitcoin price and parameters
        bitcoin_price = 25000

        for year in range(years):
            # Introduce a four-year business cycle pattern
            if year % 4 == 0:
                # Bitcoin halving event (reduce supply)
                bitcoin_price *= 2  # Adjust this factor as needed
            else:
                # Other years
                avg_return, std_dev = adjust_bitcoin_params(bitcoin_price)
                new_return = random.gauss(avg_return, std_dev)
                bitcoin_price *= (1 + new_return)

            # Restrict the maximum price to $10,000,000
            bitcoin_price = min(bitcoin_price, 10000000)

        # Store the final Bitcoin price at the end of each simulation
        final_bitcoin_prices.append(bitcoin_price)

    return final_bitcoin_prices

# Simulate Bitcoin prices and returns for 1000 simulations with a four-year business cycle
final_bitcoin_prices_business_cycle = simulate_bitcoin_price_with_business_cycle()

# Plot a histogram of the final Bitcoin prices with a four-year business cycle
plt.figure(figsize=(10, 5))
plt.hist(final_bitcoin_prices_business_cycle, bins=30, edgecolor='k', alpha=0.7)
plt.xlabel('Final Bitcoin Price (with Business Cycle)')
plt.ylabel('Frequency')
plt.title('Histogram of Final Bitcoin Prices after 40 Years (1000 Simulations) with a Four-Year Business Cycle')
plt.grid(True)
plt.show()