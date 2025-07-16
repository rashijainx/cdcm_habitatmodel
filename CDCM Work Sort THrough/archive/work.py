import matplotlib.pyplot as plt
import numpy as np

# --- Generate Data for Linear Relationship ---
# Set a random seed for reproducibility
np.random.seed(42)

# Generate x values
x = np.linspace(0, 10, 100) # 100 points from 0 to 10

# Generate y values based on a linear equation y = mx + c
m = 2.5  # Slope
c = 5    # Intercept
y_true = m * x + c

# Add some random noise to make it look more realistic
noise = np.random.normal(loc=0, scale=5, size=x.shape) # Gaussian noise
y_noisy = y_true + noise

# --- Create the Plot ---
plt.figure(figsize=(8, 6)) # Set the figure size

# Scatter plot of the noisy data
plt.scatter(x, y_noisy, label='Noisy Data Points', alpha=0.7)

# Plot the true underlying line (optional, for comparison)
plt.plot(x, y_true, color='red', linestyle='--', label='True Linear Relationship (y = 2.5x + 5)')

# --- Add Labels and Title ---
plt.title('Plot Showing a Linear Relationship with Noise')
plt.xlabel('Independent Variable (X)')
plt.ylabel('Dependent Variable (Y)')
plt.legend() # Show the legend
plt.grid(True) # Add a grid

# --- Show the Plot ---
plt.show()