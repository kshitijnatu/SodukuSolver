import time
from abc import ABC, abstractmethod
from builtins import range
import numpy as np
from numpy import load

N = 9


def load_grid(file_name):
    """
    Reading a sudoku game from a text file
    """
    # Initialize a 9x9 array and fill it with 0 value
    grid = np.zeros((9, 9), dtype=int)

    # Your code here
    # start here

    with open(file_name, 'r') as file:
        for i in range(9):
            grid[i] = file.readline().split(" ")
    # end here
    return grid


class SudokuResolver(ABC):
    def __init__(self, grid):
        """
        Initialize the resolver with a grid.
        """
        self.grid = np.copy(grid)

    @abstractmethod
    def try_num(self, row: int, col: int) -> bool:
        """
        Recursive Function to try assign a value to a cell
        """
        pass

    def find_solution(self) -> bool:
        """
        In this function, we will start with cell(0, 0) and go on to find a solution
        """
        st = time.time()
        result = self.try_num(0, 0)
        et = time.time()
        elapsed_time = et - st
        print('Execution time:', elapsed_time, 'seconds')
        print()
        return result

    def print_grid(self):
        """
        Printing the grid
        """
        for i in range(N):
            for j in range(N):
                print(self.grid[i][j], end=" ")
            print()

    def alldiff(self, arr):
        """
        Check if all values in an array are different from 1 to 9
        """
        temp_set = set(list(range(1, N + 1, 1)))
        try:
            for i in arr:
                temp_set.remove(i)
            if len(temp_set) > 0:
                return False
        except:
            return False
        return True

    def get_square_arr(self, square_index):
        """
        Get square values by index, then convert it into an array
        """
        start_row = int(square_index / 3) * 3
        start_col = (square_index % 3) * 3
        arr = self.grid[start_row: start_row + 3, start_col: start_col + 3].reshape(-1)
        return arr

    def check_grid(self):
        """
        Check if the currrent grid is a good solution
        """
        result = True
        for i in range(N):
            # Check alldiff in a row
            result = result and self.alldiff(self.grid[i, :])
            # Check alldiff in a col
            result = result and self.alldiff(self.grid[:, i].reshape(-1))
            # Check alldiff in a square
            result = result and self.alldiff(self.get_square_arr(i))

        return result


class BaseSudokuResolver(SudokuResolver):
    def is_safe_in_row(self, row: int, num: int) -> bool:
        """
        Checking if a number is not filled in a row yet
        Return: bool
        """
        # start here
        return num not in self.grid[row]
        # end here

    def is_safe_in_col(self, col: int, num: int) -> bool:
        """
        Checking if a number is not filled in a col yet
        Return: bool
        """
        # start here
        return num not in self.grid[range(N), col].reshape(-1)
        # end here

    def square_from_position(self, row: int, col: int) -> int:
        """
        Find the square index from row and col value
        """
        # start here
        return ((row // 3) * 3) + (col // 3)
        # end here

    def is_safe_in_square(self, square: int, num: int) -> bool:
        """
        Checking if a number is not filled in a square yet
        Return: bool
        """
        # start here
        return num not in self.get_square_arr(square)
        # end here

    def is_safe_num(self, row: int, col: int, num: int) -> bool:
        """
        Checking if a number is good to fill in a cell(row, col)
        Return: bool
        """
        return self.is_safe_in_row(row, num) and self.is_safe_in_col(col, num) and self.is_safe_in_square(
            self.square_from_position(row, col), num)
        # end here

    def try_num(self, row: int, col: int) -> bool:
        return False


class SimpleSudokuResolver(BaseSudokuResolver):
    def try_num(self, row, col):
        """
    This is a Recursive Function to find a number to fill into a cell(row, col).
    We will start with the cell(0, 0)

    Return:
      - True if found a solution
      - False if no solution found
    """
        if row == N - 1 and col == N:
            return True

        if col == N:
            row += 1
            col = 0

        if self.grid[row][col] > 0:
            return self.try_num(row, col + 1)
        for i in range(1, N + 1, 1):
            if self.is_safe_num(row, col, i):
                self.grid[row][col] = i
                if self.try_num(row, col + 1):
                    return True
            self.grid[row][col] = 0
        return False
        # end here


class ImprovedSudokuResolver(BaseSudokuResolver):
    def __init__(self, grid):
        super().__init__(grid)

        self.avai_rows = [set(list(range(1, N + 1, 1))) for i in range(N)]
        self.avai_cols = [set(list(range(1, N + 1, 1))) for i in range(N)]
        self.avai_squares = [set(list(range(1, N + 1, 1))) for i in range(N)]

        ## Compute 3 avail arrays
        # start here
        for i in range(N):
            for _ in range(N):
                tempRowNum = self.avai_rows[i].pop()
                tempColNum = self.avai_cols[i].pop()
                tempSquareNum = self.avai_squares[i].pop()

                if self.is_safe_in_row(i, tempRowNum):
                    self.avai_rows[i].add(tempRowNum)
                if self.is_safe_in_col(i, tempColNum):
                    self.avai_cols[i].add(tempColNum)
                if self.is_safe_in_square(i, tempSquareNum):
                    self.avai_squares[i].add(tempSquareNum)
        # end here

    def try_num(self, row: int, col: int) -> bool:
        if row == N - 1 and col == N:
            return True

        if col == N:
            row += 1
            col = 0

        if self.grid[row][col] > 0:
            return self.try_num(row, col + 1)
        square_index = self.square_from_position(row, col)
        for i in self.avai_rows[row] & self.avai_cols[col] & self.avai_squares[square_index]:
            self.avai_rows[row].remove(i)
            self.avai_cols[col].remove(i)
            self.avai_squares[square_index].remove(i)

            if self.is_safe_num(row, col, i):
                self.grid[row][col] = i
                if self.try_num(row, col + 1):
                    return True
            self.grid[row][col] = 0

            self.avai_rows[row].add(i)
            self.avai_cols[col].add(i)
            self.avai_squares[square_index].add(i)
        return False
        # end here


grid_easy_from_txt = load_grid("sudoku_easy.txt")
grid_expert_from_txt = load_grid("sudoku_expert.txt")

solver1 = ImprovedSudokuResolver(grid_easy_from_txt)
solver2 = ImprovedSudokuResolver(grid_expert_from_txt)

if solver1.find_solution() and solver1.check_grid():
    print("Found a solution:")
    solver1.print_grid()
else:
    print("No solution or invalid solution found!")

if solver2.find_solution() and solver2.check_grid():
    print("Found a solution:")
    solver2.print_grid()
else:
    print("No solution or invalid solution found!")
