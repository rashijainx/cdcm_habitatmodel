from pytest import approx

from lunar_hab.basic_math.math_functions import (
    calculate_product,
    calculate_cube,
    calculate_square
)

# Calculate Products 
def test_calculate_product_positive():
    result = calculate_product(2, 3, 4)
    assert result == 24


def test_calculate_product_negative():
    result = calculate_product(-2, 3, 4)
    assert result == -24

def test_calculate_product_zero():
    result = calculate_product(5, 0, 10)
    assert result == 0

def test_calculate_product_fraction():
    result = calculate_product(0.1, 1)
    assert result == approx(0.1)


# Calculate Square
def test_calculate_square_positive():
    result = calculate_square(2)
    assert result == 4

def test_calculate_square_negative():
    result = calculate_square(-2)
    assert result == 4

def test_calculate_square_zero():
    result = calculate_square(0)
    assert result == 0

def test_calculate_square_fraction():
    result = calculate_square(0.2)
    assert result == approx(0.04)

# Calculate Cube
def test_calculate_cube_positive():
    result = calculate_cube(2)
    assert result == 8

def test_calculate_cube_negative():
    result = calculate_cube(-2)
    assert result == -8

def test_calculate_cube_zero():
    result = calculate_cube(0)
    assert result == 0

def test_calculate_cube_fraction():
    result = calculate_cube(0.2)
    assert result == approx(0.008)