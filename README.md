# python-SudokuSolver
Classes and functions to represent and solve of traditional Sudoku puzzles of arbitrary box dimensions. A video demonstrating use of this project can be found in this [video demo](https://youtu.be/jNQXAC9IVRw).

## Description

This project is built around the Sudoku class in src/sudoku_solver/sudoku_solver_class.py. This is a class used to represent Sudoku puzzles and solve them.

There are currently two main ways to load a Sudoku as a Sudoku object:
1) Directly initializing the Sudoku object, manually providing the box size and the initial Sudoku board.
2) Loading the Sudoku board from a specially formatted .csv file (examples of which are contained in the subfolders of src/sudoku_csv_files) using the class method Sudoku.loadSudokuFromCSV().

Once loaded, a formatted version of the Sudoku board can then be printed to console using the print command.

However, the main feature of the Sudoku class is its ability to solve the Sudoku.

## Usage

Here, examples are given as to basic use of the module. These make use of the following 3x3 Sudoku:

<pre>
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
</pre>

which is the Sudoku stored in:

[src/sudoku_csv_files/three_by_three/easy3x3_1.csv](src/sudoku_csv_files/three_by_three/easy3x3_1.csv)

This has a unique solution (with the initially set elements in bold):
<pre>
 -----------------------------
┆ <b>7</b>  <b>8</b>  5 │ <b>4</b>  3  9 │ <b>1</b>  <b>2</b>  6 ┆
┆ <b>6</b>  1  2 │ 8  <b>7</b>  <b>5</b> │ 3  4  <b>9</b> ┆
┆ 4  9  3 │ <b>6</b>  2  <b>1</b> │ 5  <b>7</b>  <b>8</b> ┆
┆─────────┼─────────┼─────────┆
┆ 8  5  <b>7</b> │ 9  <b>4</b>  3 │ <b>2</b>  <b>6</b>  1 ┆
┆ 2  6  <b>1</b> │ 7  <b>5</b>  8 │ <b>9</b>  <b>3</b>  4 ┆
┆ <b>9</b>  3  <b>4</b> │ 1  <b>6</b>  2 │ 7  8  <b>5</b> ┆
┆─────────┼─────────┼─────────┆
┆ 5  <b>7</b>  8 │ <b>3</b>  9  4 │ 6  <b>1</b>  <b>2</b> ┆
┆ <b>1</b>  <b>2</b>  6 │ 5  8  <b>7</b> │ <b>4</b>  9  3 ┆
┆ 3  <b>4</b>  <b>9</b> │ <b>2</b>  1  <b>6</b> │ 8  5  <b>7</b> ┆
 -----------------------------
</pre>
In the following examples, when loading from .csv files it is assumed the local directory is the directory of this README.md file, and the file referenced contains the above Sudoku.

### Use within other Python programs and scripts

The following example shows 

### Use as a script

This may also be run as a script, which finds the solution or solutions to a Sudoku contained in a .csv file using the following syntax:

```bash
$ python src/sudoku_solver/sudoku_solver_class.py <Sudoku csv file path> [-s]
```

The optional flag '-s', if used, indicates that only a single solution should be sought for, (with the search abandoned if and when the first valid solution is identified). If this flag is not used, then all possible solutions will be found.

This console command then performs the following steps:
1) Loads the Sudoku from the .csv file at the given location as a Sudoku object. If this is unsuccessful, a message declaring the reason is printed and the script ends.
2) Prints the initial Sudoku to the console, labelled as the Initial Sudoku
3) Depending on the use of the '-s' flag:
    - If the '-s' flag was not used then all possible solutions to the Sudoku are found and printed to console, with the $n$:th Sudoku found labelled as 'Solution $n$'. Following completion of the search, the number of solutions found is printed to console.
    - If the '-s' flag was used then a single solution, if any exist is printed to console, labelled as 'Solution'.
4) Finally, the total time taken to find the solution or solutions is printed to console and the script ends.

For example, using the example Sudoku .csv file [easy3x3_1.csv](src/sudoku_csv_files/three_by_three/easy3x3_1.csv) (full path given above), use of the script without and with the '-s' flag results in the respective following outputs:

```bash
$ python src/sudoku_solver/sudoku_solver_class.py src/sudoku_csv_files/three_by_three/easy3x3_1.csv
```
<pre>
Initial Sudoku:
 -----------------------------
┆ <b>7</b>  <b>8</b>    │ <b>4</b>       │ <b>1</b>  <b>2</b>    ┆
┆ <b>6</b>       │    <b>7</b>  <b>5</b> │       <b>9</b> ┆
┆         │ <b>6</b>     <b>1</b> │    <b>7</b>  <b>8</b> ┆
┆─────────┼─────────┼─────────┆
┆       <b>7</b> │    <b>4</b>    │ <b>2</b>  <b>6</b>    ┆
┆       <b>1</b> │    <b>5</b>    │ <b>9</b>  <b>3</b>    ┆
┆ <b>9</b>     <b>4</b> │    <b>6</b>    │       <b>5</b> ┆
┆─────────┼─────────┼─────────┆
┆    <b>7</b>    │ <b>3</b>       │    <b>1</b>  <b>2</b> ┆
┆ <b>1</b>  <b>2</b>    │       <b>7</b> │ <b>4</b>       ┆
┆    <b>4</b>  <b>9</b> │ <b>2</b>     <b>6</b> │       <b>7</b> ┆
 -----------------------------
Solution 1
 -----------------------------
┆ <b>7</b>  <b>8</b>  5 │ <b>4</b>  3  9 │ <b>1</b>  <b>2</b>  6 ┆
┆ <b>6</b>  1  2 │ 8  <b>7</b>  <b>5</b> │ 3  4  <b>9</b> ┆
┆ 4  9  3 │ <b>6</b>  2  <b>1</b> │ 5  <b>7</b>  <b>8</b> ┆
┆─────────┼─────────┼─────────┆
┆ 8  5  <b>7</b> │ 9  <b>4</b>  3 │ <b>2</b>  <b>6</b>  1 ┆
┆ 2  6  <b>1</b> │ 7  <b>5</b>  8 │ <b>9</b>  <b>3</b>  4 ┆
┆ <b>9</b>  3  <b>4</b> │ 1  <b>6</b>  2 │ 7  8  <b>5</b> ┆
┆─────────┼─────────┼─────────┆
┆ 5  <b>7</b>  8 │ <b>3</b>  9  4 │ 6  <b>1</b>  <b>2</b> ┆
┆ <b>1</b>  <b>2</b>  6 │ 5  8  <b>7</b> │ <b>4</b>  9  3 ┆
┆ 3  <b>4</b>  <b>9</b> │ <b>2</b>  1  <b>6</b> │ 8  5  <b>7</b> ┆
 -----------------------------

This Sudoku has exactly 1 solution
time to search for all possible solutions = 0.0364 seconds
</pre>

```bash
$ python src/sudoku_solver/sudoku_solver_class.py src/sudoku_csv_files/three_by_three/easy3x3_1.csv -s
```
<pre>
Initial Sudoku:
 -----------------------------
┆ <b>7</b>  <b>8</b>    │ <b>4</b>       │ <b>1</b>  <b>2</b>    ┆
┆ <b>6</b>        │    <b>7</b>  <b>5</b> │       <b>9</b> ┆
┆         │ <b>6</b>     <b>1</b> │    <b>7</b>  <b>8</b> ┆
┆─────────┼─────────┼─────────┆
┆       <b>7</b> │    <b>4</b>    │ <b>2</b>  <b>6</b>    ┆
┆       <b>1</b> │    <b>5</b>    │ <b>9</b>  <b>3</b>    ┆
┆ <b>9</b>     <b>4</b> │    <b>6</b>    │       <b>5</b> ┆
┆─────────┼─────────┼─────────┆
┆    <b>7</b>    │ <b>3</b>       │    <b>1</b>  <b>2</b> ┆
┆ <b>1</b>  <b>2</b>    │       <b>7</b> │ <b>4</b>       ┆
┆    <b>4</b>  <b>9</b> │ <b>2</b>     <b>6</b> │       <b>7</b> ┆
 -----------------------------
Solution
 -----------------------------
┆ <b>7</b>  <b>8</b>  5 │ <b>4</b>  3  9 │ <b>1</b>  <b>2</b>  6 ┆
┆ <b>6</b>  1  2 │ 8  <b>7</b>  <b>5</b> │ 3  4  <b>9</b> ┆
┆ 4  9  3 │ <b>6</b>  2  <b>1</b> │ 5  <b>7</b>  <b>8</b> ┆
┆─────────┼─────────┼─────────┆
┆ 8  5  <b>7</b> │ 9  <b>4</b>  3 │ <b>2</b>  <b>6</b>  1 ┆
┆ 2  6  <b>1</b> │ 7  <b>5</b>  8 │ <b>9</b>  <b>3</b>  4 ┆
┆ <b>9</b>  3  <b>4</b> │ 1  <b>6</b>  2 │ 7  8  <b>5</b> ┆
┆─────────┼─────────┼─────────┆
┆ 5  <b>7</b>  8 │ <b>3</b>  9  4 │ 6  <b>1</b>  <b>2</b> ┆
┆ <b>1</b>  <b>2</b>  6 │ 5  8  <b>7</b> │ <b>4</b>  9  3 ┆
┆ 3  <b>4</b>  <b>9</b> │ <b>2</b>  1  <b>6</b> │ 8  5  <b>7</b> ┆
 -----------------------------
total search time before finding a solution = 0.0359 seconds
</pre>

Note that the values set in the initial Sudoku are marked in bold for all printed Sudokus, including the printing of the initial Sudoku itself (resulting in all of its non-empty elements being bold).

## Dependencies

- Python 3.11
- sortedcontainers
- numpy
- pytest

## Brief overview of solution method

The method used in the solution of the Sudoku makes use a combination of the following techniques and data structures:
1) Recursive backtracking
2) Bitmasks (including use of bitwise operations)
3) 2-dimensional arrays (specifically numpy arrays), including array slicing
4) Sorted containers (specifically SortedDict from the sortedcontainers package)
5) Stacks (implemented as a Python list)

## Potential future developments
This project has been built with the potential for further optimisation and expansion in the future, and is very much a starting point, either for further development of the Sudoku class itself or through descendant classes. Ideas for such future work include:
1) Further optimisation of the solution algorithm, specifically the simplification stage. This may include implementation of known intermediate and advanced solving techniques such as hidden or naked pairs and triples, X-wing, swordfish etc.
2) Implementing a GUI, for example using tkinter or pygame
3) Allowing the user to attempt to solve the Sudoku, with the potential for spotting mistakes made by the user. This would be more user friendly if done using a GUI.

## License

[MIT License](LICENSE)