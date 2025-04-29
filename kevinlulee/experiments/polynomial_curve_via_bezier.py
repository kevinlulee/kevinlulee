import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb

def polynomial_to_power_coefficients_reparameterized(poly_coeffs, a, b):
    """
    Converts polynomial coefficients from power basis in x to power basis in t
    where x = a + (b-a)t, for t in [0, 1].

    Args:
        poly_coeffs (list): Coefficients of the polynomial P(x) in power basis [c0, c1, ..., cn].
                            P(x) = c0 + c1*x + c2*x^2 + ... + cn*x^n.
        a (float): The start of the interval for x.
        b (float): The end of the interval for x.

    Returns:
        list: Coefficients of the polynomial Q(t) = P(a + (b-a)t) in power basis [d0, d1, ..., dn].
              Q(t) = d0 + d1*t + d2*t^2 + ... + dn*t^n.
    """
    n = len(poly_coeffs) - 1
    d_coeffs = [0.0] * (n + 1)
    for j in range(n + 1):
        for k in range(j, n + 1):
            # Coefficient of t^j in the expansion of c_k * (a + (b-a)t)^k
            d_coeffs[j] += poly_coeffs[k] * comb(k, j) * (a**(k - j)) * ((b - a)**j)
    return d_coeffs

def power_to_bernstein_coefficients(d_coeffs):
    """
    Converts polynomial coefficients from power basis in t to Bernstein basis in t.

    Args:
        d_coeffs (list): Coefficients of the polynomial Q(t) in power basis [d0, d1, ..., dn].
                         Q(t) = d0 + d1*t + d2*t^2 + ... + dn*t^n.

    Returns:
        list: Coefficients of the polynomial Q(t) in Bernstein basis [b0, b1, ..., bn].
              Q(t) = sum(bi * B_{i,n}(t)) where B_{i,n}(t) are Bernstein basis polynomials.
              These are the y-coordinates of the control points.
    """
    n = len(d_coeffs) - 1
    b_coeffs = [0.0] * (n + 1)
    for i in range(n + 1):
        for j in range(i + 1):
             b_coeffs[i] += d_coeffs[j] * comb(i, j) / comb(n, j)
    return b_coeffs

def bezier_curve_points(control_points, num_points=100):
    """
    Generates points on a Bezier curve defined by control points using the
    Bernstein polynomial definition.

    Args:
        control_points (list): List of (x, y) tuples for the control points.
        num_points (int): Number of points to generate on the curve.

    Returns:
        tuple: Two lists, x_points and y_points.
    """
    n = len(control_points) - 1
    t_values = np.linspace(0, 1, num_points)
    curve_points = []
    for t in t_values:
        point_x = 0
        point_y = 0
        for i in range(n + 1):
            bernstein_basis = comb(n, i) * (t**i) * ((1 - t)**(n - i))
            point_x += bernstein_basis * control_points[i][0]
            point_y += bernstein_basis * control_points[i][1]
        curve_points.append((point_x, point_y))
    return zip(*curve_points)

def draw_polynomial_as_bezier(poly_coeffs, interval, num_bezier_points=100):
    """
    Draws a polynomial equation as a Bezier curve over a given interval.

    Args:
        poly_coeffs (list): Coefficients of the polynomial P(x) in power basis [c0, c1, ..., cn].
                            P(x) = c0 + c1*x + c2*x^2 + ... + cn*x^n.
        interval (tuple): A tuple (a, b) representing the interval for x.
        num_bezier_points (int): Number of points to use for drawing the Bezier curve.
    """
    a, b = interval
    n = len(poly_coeffs) - 1

    # 1. Get power basis coefficients of P(a + (b-a)t)
    d_coeffs = polynomial_to_power_coefficients_reparameterized(poly_coeffs, a, b)

    # 2. Convert power basis coefficients to Bernstein basis coefficients (y-coordinates of control points)
    y_control_points = power_to_bernstein_coefficients(d_coeffs)

    # 3. Define the control points with evenly spaced x-coordinates
    x_control_points = [a + i * (b - a) / n for i in range(n + 1)]
    control_points = list(zip(x_control_points, y_control_points))

    # 4. Generate points on the Bezier curve
    bezier_x, bezier_y = bezier_curve_points(control_points, num_bezier_points)

    # 5. Plot the results
    plt.figure()
    plt.plot(bezier_x, bezier_y, label=f'Bezier Curve (degree {n})')

    # Plot the original polynomial for comparison
    x_values = np.linspace(a, b, 100)
    # np.polyval expects coefficients in decreasing order of power [cn, cn-1, ..., c0]
    y_values = np.polyval(poly_coeffs[::-1], x_values)
    plt.plot(x_values, y_values, '--', label='Original Polynomial')

    plt.scatter(*zip(*control_points), color='red', label='Control Points')
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Polynomial represented by a Bezier Curve')
    plt.grid(True)
    plt.show()

# Example Usage: Draw the polynomial f(x) = x^2 on the interval [0, 1]
# Coefficients are [0, 0, 1] for c0 + c1*x + c2*x^2
poly_coeffs_example1 = [0, 0, 1]
interval_example1 = (0, 1)
draw_polynomial_as_bezier(poly_coeffs_example1, interval_example1)

# Example Usage: Draw the polynomial f(x) = x^3 - x on the interval [-2, 2]
# Coefficients are [0, -1, 0, 1] for c0 + c1*x + c2*x^2 + c3*x^3
poly_coeffs_example2 = [0, -1, 0, 1]
interval_example2 = (-2, 2)
draw_polynomial_as_bezier(poly_coeffs_example2, interval_example2)

# Example Usage: Draw the polynomial f(x) = 0.5x^2 + 2x + 1 on the interval [-3, 1]
# Coefficients are [1, 2, 0.5] for c0 + c1*x + c2*x^2
poly_coeffs_example3 = [1, 2, 0.5]
interval_example3 = (-3, 1)
draw_polynomial_as_bezier(poly_coeffs_example3, interval_example3)
