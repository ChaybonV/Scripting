def generate():
    depth = int(input())
    print(depth)
    triangle = []

    for i in range(depth):
        row = []
        for j in range(i + 1):
            if j == 0 or j == i:
                row.append(1)
            else:
                row.append(triangle[i - 1][j - 1] + triangle[i - 1][j])
        triangle.append(row)

    for row in triangle:
        for number in range(len(row)):
            if number == len(row) - 1:
                print(row[number])
            else:
                print(row[number], end=" ")

    return triangle

def prime(row, triangle):
    print(row)
    row_index = row - 1  # row 1 is index 0

    if row_index < 0 or row_index >= len(triangle):
        return False

    row_data = triangle[row_index]

    for number in row_data[1:-1]:
        if number % row_index != 0:
            return False
        
    return True

def reflect(triangle):
    reflected = triangle[::-1]
    
    for row in reflected:
        for number in range(len(row)):
            if number == len(row) - 1:
                print(row[number])
            else:
                print(row[number], end=" ")

    return reflected

def binary(triangle):
    binary_triangle = []
    for row in triangle:
        binary_row = []
        for num in row:
            if num % 2 == 0:
                binary_row.append(0)
            else:
                binary_row.append(1)
        binary_triangle.append(binary_row)

    for row in binary_triangle:
        for number in range(len(row)):
            if number == len(row) - 1:
                print(row[number])
            else:
                print(row[number], end=" ")

    return binary_triangle


if __name__ == "__main__":
    print("Pascal's Triangle:")
    print("Depth:")
    triangle = generate()
    
    print("Prime row:")
    print(prime(int(input()), triangle))

    print("Reflected Triangle:")
    reflect(triangle)

    print("Binary Triangle:")
    binary(triangle)

# Chaybon Verlooy
# BADI 1 - Scripting