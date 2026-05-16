# python-SudokuSolver
Classes and functions to represent and solve of traditional Sudoku puzzles of arbitrary box dimensions. A video demonstrating use of this project can be found in this [video demo](https://youtu.be/jNQXAC9IVRw).

### Description

This project is built around the Sudoku class in src/sudoku_solver/sudoku_solver_class.py. This is a class used to represent Sudoku puzzles and solve them.

There are currently two main ways to load a Sudoku as a Sudoku object:
1) Directly initializing the Sudoku object, manually providing the box size and the initial Sudoku board.
2) Loading the Sudoku board from a specially formatted .csv file (examples of which are contained in the subfolders of src/sudoku_csv_files) using the class method Sudoku.loadSudokuFromCSV().

Once loaded, a formatted version of the Sudoku board can then be printed to console using the print command.

However, the main feature of the Sudoku class is its ability to solve the Sudoku.

### How to use

Here, examples are given as to basic use of the module. These make use of the following 3x3 Sudoku, which is the Sudoku stored in src/sudoku_csv_files/three_by_three/easy3x3_1.csv:

```
 -----------------------------
┆ 7  8    │ 4       │ 1  2    ┆
┆ 6       │    7  5 │       9 ┆
┆         │ 6     1 │    7  8 ┆
┆─────────┼─────────┼─────────┆
┆       7 │    4    │ 2  6    ┆
┆       1 │    5    │ 9  3    ┆
┆ 9     4 │    6    │       5 ┆
┆─────────┼─────────┼─────────┆
┆    7    │ 3       │    1  2 ┆
┆ 1  2    │       7 │ 4       ┆
┆    4  9 │ 2     6 │       7 ┆
 -----------------------------
```

This has a unique solution (with the initially set elements in bold):

```
 -----------------------------
┆ **7**  **8**  5 │ **4**  3  9 │ **1**  **2**  6 ┆
┆ **6**  1  2 │ 8  **7**  **5** │ 3  4  **9** ┆
┆ 4  9  3 │ **6**  2  **1** │ 5  **7**  **8** ┆
┆─────────┼─────────┼─────────┆
┆ 8  5  **7** │ 9  **4**  3 │ **2**  **6**  1 ┆
┆ 2  6  **1** │ 7  **5**  8 │ **9**  **3**  4 ┆
┆ **9**  3  **4** │ 1  **6**  2 │ 7  8  **5** ┆
┆─────────┼─────────┼─────────┆
┆ 5  **7**  8 │ **3**  9  4 │ 6  **1**  **2** ┆
┆ **1**  **2**  6 │ 5  8  **7** │ **4**  9  3 ┆
┆ 3  **4**  **9** │ **2**  1  **6** │ 8  5  **7** ┆
 -----------------------------
```

In the following examples, when loading from .csv files it is assumed the local directory is the directory of this README.md file, and the file referenced contains the above Sudoku.

#### Use within other Python programs and scripts

The following example shows 

#### Use as a script


### Brief overview of solution method


### Possible future developments
This project has been built with the potential for further optimisation and expansion in the future, and is very much a starting point, either for further development of the Sudoku class itself or through descendant classes. Ideas for such future work include:
1) Further optimisation of the solution algorithm, specifically the simplification stage. This may include implementation of known intermediate and advanced solving techniques such as hidden or naked pairs and triples, X-wing, swordfish etc.
2) Implementing a GUI, for example using tkinter or pygame
3) Allowing the user to attempt to solve the Sudoku, with the potential for spotting mistakes made by the user. This would be more user friendly if done using a GUI.