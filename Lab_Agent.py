import random
import matplotlib.pyplot as plt


# Utility functions
def select_from_dist(item_prob_dist):
    """
    Selects an item from a probability distribution.
    item_prob_dist: dictionary of item:probability (probabilities must sum to 1).
    """
    ranreal = random.random()
    for item, prob in item_prob_dist.items():
        if ranreal < prob:
            return item
        ranreal -= prob
    raise RuntimeError(f"{item_prob_dist} is not a valid probability distribution")


# Plotting Class
class PlotHistory:
    """
    Handles the plotting of price, stock levels, and orders over time.
    """
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment

    def plot_history(self):
        """Plots price and stock level history along with the agent's purchase decisions."""
        plt.figure(figsize=(10, 6))  # Set the size of the plot

        # Plot price history with a blue line
        plt.subplot(2, 1, 1)  # First subplot for price history
        plt.plot(self.environment.price_history, label="Price", color='blue')  # Use blue for the price line
        plt.ylabel("Price")  # Y-axis label for price
        plt.legend()  # Display legend

        # Plot stock levels and buying decisions with orange bars
        plt.subplot(2, 1, 2)  # Second subplot for stock levels and purchases
        plt.plot(self.environment.stock_history, label="Stock Level", color='blue')  # Use blue for stock levels
        plt.bar(range(len(self.agent.buy_history)), self.agent.buy_history, label="Purchased", color='orange', alpha=0.7)  # Use orange for purchases
        plt.ylabel("Stock / Purchases")  # Y-axis label for stock and purchases
        plt.legend()  # Display legend

        plt.xlabel("Time")  # X-axis label for time
        plt.tight_layout()  # Adjust layout for better spacing
        plt.show()  # Render the plot


# Environment Class
class SmartphoneEnvironment:
    """
    Simulates the inventory and price dynamics of a smartphone store.
    """
    price_delta = [10, -20, 5, -15, 0, 25, -30, 20, -5, 0]  # Simulates price fluctuations
    noise_sd = 5  # Random price noise standard deviation

    def __init__(self):
        self.time = 0
        self.stock = 50  # Initial stock
        self.price = 600  # Initial price
        self.stock_history = [self.stock]  # Tracks stock over time
        self.price_history = [self.price]  # Tracks price over time

    def initial_percept(self):
        """Returns the initial percept (price and stock level)."""
        return {"price": self.price, "stock": self.stock}

    def do_action(self, action):
        """
        Executes the agent's action and updates the environment.
        action: Dictionary containing 'buy' (number of units to purchase).
        """
        # Simulate random sales (units sold daily)
        daily_sales = select_from_dist({3: 0.2, 5: 0.3, 7: 0.3, 10: 0.2})
        bought = action.get("buy", 0)  # Units ordered by the agent
        self.stock = max(0, self.stock + bought - daily_sales)  # Update stock

        # Update price with random fluctuations
        self.time += 1
        self.price += self.price_delta[self.time % len(self.price_delta)] + random.gauss(0, self.noise_sd)

        # Append to history
        self.stock_history.append(self.stock)
        self.price_history.append(self.price)

        # Return the updated percept
        return {"price": self.price, "stock": self.stock}


# Agent Class
class SmartphoneAgent:
    """
    An agent that manages inventory based on price and stock level.
    """
    def __init__(self):
        self.average_price = 600  # Initial average price
        self.buy_history = []  # Tracks buying decisions
        self.total_spent = 0  # Tracks total expenditure

    def select_action(self, percept):
        """
        Determines the action (number of units to order) based on the percept.
        percept: Dictionary containing 'price' and 'stock'.
        """
        current_price = percept["price"]
        current_stock = percept["stock"]

        # Update average price (using exponential moving average)
        self.average_price += (current_price - self.average_price) * 0.1

        # Decision-making process
        if current_price < 0.8 * self.average_price and current_stock > 10:
            # If price is 20% below average and stock is not critically low
            tobuy = 15
        elif current_stock < 10:
            # If stock level is critical
            tobuy = 10
        else:
            # No need to purchase
            tobuy = 0

        # Track expenditure and decisions
        self.total_spent += tobuy * current_price
        self.buy_history.append(tobuy)

        # Return the action
        return {"buy": tobuy}


# Simulation Class
class Simulation:
    """
    Simulates the interaction between the agent and the environment.
    """
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment
        self.percept = self.environment.initial_percept()

    def run(self, steps):
        """
        Runs the simulation for a specified number of steps.
        steps: Number of time steps to simulate.
        """
        for step in range(steps):
            # Agent decides an action based on the percept
            action = self.agent.select_action(self.percept)

            # Environment updates based on the action
            self.percept = self.environment.do_action(action)


# Main Simulation Execution
if __name__ == "__main__":
    # Create environment and agent
    environment = SmartphoneEnvironment()
    agent = SmartphoneAgent()

    # Run simulation
    simulation = Simulation(agent, environment)
    simulation.run(50)  # Run for 50 time steps

    # Plot the results
    plotter = PlotHistory(agent, environment)
    plotter.plot_history()