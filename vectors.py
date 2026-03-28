import math

class Vector:
    def __init__(self, magnitude=None, direction=None, vector=None):
        if vector is not None:
            self._vector = tuple(vector)
        elif magnitude is not None and direction is not None:
            if all(x == 0 for x in direction):
                raise ValueError("Direction cannot be a zero vector")
            self._vector = tuple(magnitude * x for x in direction)
        else:
            self._vector = tuple()

    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, value):
        self._vector = tuple(value)

    @property
    def magnitude(self):
        return math.sqrt(sum(x*x for x in self._vector))

    @property
    def direction(self):
        if self.is_zero():
            return None
        mag = self.magnitude
        return tuple(x / mag for x in self._vector)

    @property
    def dimension(self):
        return len(self._vector)

    def is_zero(self):
        return all(x == 0 for x in self._vector)

    # Sequence behavior
    def __getitem__(self, index):
        return self._vector[index]

    def __len__(self):
        return len(self._vector)

    def __iter__(self):
        return iter(self._vector)

    # String representations
    def __str__(self):
        return f"Magnitude: {self.magnitude}, Direction: {self.direction}, Vector: {self.vector}"
    
    def __repr__(self):
        return f"Vector({self._vector})"

    # Arithmetic operations
    def __add__(self, other):
        if not isinstance(other, Vector):
            raise TypeError("Can only add Vector to Vector")
        if len(self) != len(other):
            raise ValueError("Vectors must have the same dimension")
        return Vector(vector=tuple(x + y for x, y in zip(self, other)))

    def __sub__(self, other):
        if not isinstance(other, Vector):
            raise TypeError("Can only subtract Vector from Vector")
        if len(self) != len(other):
            raise ValueError("Vectors must have the same dimension")
        return Vector(vector=tuple(x - y for x, y in zip(self, other)))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(vector=tuple(x * other for x in self))
        raise TypeError("Only scalar multiplication allowed")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return Vector(vector=tuple(x / other for x in self))
        raise TypeError("Vector can only be divided by a scalar")

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        if len(self) != len(other):
            return False
        return all(abs(a - b) < 1e-9 for a, b in zip(self, other))

    def __neg__(self):
        return Vector(vector=[-x for x in self._vector])

    def __abs__(self):
        return self.magnitude

    def __matmul__(self, other):
        return self.dotproduct(other)

    # Vector operations
    def dotproduct(self, other):
        if len(self) != len(other):
            raise ValueError("Vectors must have the same dimension")
        return sum(x*y for x, y in zip(self, other))

    def crossproduct(self, other):
        if len(self) != 3 or len(other) != 3:
            raise ValueError("Cross product only defined for 3D vectors")
        i = self[1]*other[2] - self[2]*other[1]
        j = -(self[0]*other[2] - self[2]*other[0])
        k = self[0]*other[1] - self[1]*other[0]
        return Vector(vector=(i, j, k))

    def normalize(self):
        if self.is_zero():
            raise ValueError("Cannot normalize zero vector")
        mag = self.magnitude
        return Vector(vector=tuple(x / mag for x in self))

    def angle_with(self, other, unit='radian'):
        if self.is_zero() or other.is_zero():
            raise ValueError("Cannot compute angle with zero vector")
        cos_theta = self.dotproduct(other) / (self.magnitude * other.magnitude)
        cos_theta = max(min(cos_theta, 1.0), -1.0)
        angle_rad = math.acos(cos_theta)
        if unit == 'degree':
            return math.degrees(angle_rad)
        return angle_rad

    def projection_onto(self, other):
        if other.is_zero():
            raise ValueError("Cannot project onto zero vector")
        scalar = self.dotproduct(other) / other.magnitude**2
        return other * scalar

    # Geometric features
    def is_orthogonal_to(self, other):
        return abs(self.dotproduct(other)) < 1e-9

    def is_parallel_to(self, other):
        if self.is_zero() or other.is_zero():
            return False
        ratios = []
        for a, b in zip(self._vector, other._vector):
            if b != 0:
                ratios.append(a / b)
            elif a != 0:
                return False
        if not ratios:
            return True
        return all(abs(r - ratios[0]) < 1e-9 for r in ratios)



def matrix_mult(matrix1, matrix2):
    # Check if multiplication is possible
    if len(matrix1[0]) != len(matrix2):
        raise ValueError("Number of columns of matrix1 must equal number of rows of matrix2")
    
    # Initialize result matrix with zeros
    result = [[0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix1))]
    
    # Multiply
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]
    
    return result


    


                
                
                
                
                
                


    