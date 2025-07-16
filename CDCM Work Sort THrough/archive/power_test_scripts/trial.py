import numpy as np

def solar_irradiance(t):
    # Dummy function for illustration; e.g., S(t) = sin(t)
    return np.sin(t)

def main():
    t_start = 0.0   # starting time
    t_end = 10.0    # ending time
    dt = 0.1        # time step
    t = t_start
    
    while t < t_end:
        S = solar_irradiance(t)
        # Check condition at each time step
        if S < 0:
            print("S first dips below zero at time:", t)
            break
        t += dt
    else:
        print("S never dips below zero.")

if __name__ == "__main__":
    main()
