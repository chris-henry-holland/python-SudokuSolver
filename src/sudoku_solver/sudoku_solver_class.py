
from __future__ import annotations

from typing import (
    Any,
    Generator,
    Optional,
)

import argparse
import copy
import csv
import os
import sys
import time

import numpy as np
from sortedcontainers import SortedDict


class Sudoku(object):
    """
    Class whose instances each represent a specific traditional
    Sudoku puzzle with boxes of arbitrary dimensions, including
    a method to find all possible solutions (if any) to the
    represented Sudoku.

    Attributes:
        object (_type_): _description_

        box_shape (tuple[int, int]):
        
                Note that this means that moving along a given row
                of the Sudoku, box_shape[1] different boxes are
                encountered and moving down a given column,
                box_shape[0] different boxes are encountered.

    """
    region_typ_strs = ["row", "column", "box"]

    def __init__(
        self,
        initial_board: list[list[int]],
        box_shape: tuple[int, int]=(3, 3),
    ):
        """
        Initialises a Sudoku object with a given box shape
        (as specified by box_shape) and initial set entries
        (as specified by initial_board).

        Args:
            initial_board (list[list[int]]): A list of lists of
                    integers, representing the Sudoku board, where
                    each inner list represents a row of the Sudoku
                    board. The outer list and each of the inner lists
                    must have the same number of elements as the side
                    length of the Sudoku grid (equal to the product of
                    the two box_shape dimensions, by default 9), and each
                    element of the inner list must be an integer between
                    0 and the side length of the Sudoku grid inclusive,
                    with the elements with set initial values given by
                    that strictly positive integer value and the
                    initially unset elements represented by the value
                    zero.
            box_shape (tuple[int, int], optional): 2-tuple of strictly
                    positive integers specifying the shape of the
                    sudoku boxes, where index 0 represents the number
                    of rows and index 1 represents the number of columns.
                    This determines the size of the Sudoku grid, it being
                    a square with side length equal to the product of the
                    two box_shape dimensions.
                Default: (3, 3) (the standard 9x9 Sudoku)

        Raises:
            TypeError: Raised if initial_board, its components
                    or the components of its components are not
                    of the correct type (indexable, indexable and
                    integer types respectively) or box_shape or
                    its components are not of the correct type
                    (indexable or integer types respectively).
            ValueError: Raised if the dimensions of initial_board
                    or box_shape are incorrect, if the dimensions
                    of initial_board are incompatible with box_shape,
                    if the values in initial_board or box_shape are
                    not in the permitted range or the Sudoku board
                    in initial_board contains direct conflicts (i.e.
                    a non-zero integer appears more than once in
                    a row, column or box).

        Examples:
        >>> sudoku = Sudoku(
                [
                    [7,8,0,4,0,0,1,2,0]
                    [6,0,0,0,7,5,0,0,9]
                    [0,0,0,6,0,1,0,7,8]
                    [0,0,7,0,4,0,2,6,0]
                    [0,0,1,0,5,0,9,3,0]
                    [9,0,4,0,6,0,0,0,5]
                    [0,7,0,3,0,0,0,1,2]
                    [1,2,0,0,0,7,4,0,0]
                    [0,4,9,2,0,6,0,0,7]
                ],
            )
        >>> print(sudoku)
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

        >>> sudoku = Sudoku(
                [
                    [1,2,0,4,0,5]
                    [4,6,0,0,2,0]
                    [0,0,0,6,4,1]
                    [0,4,5,3,0,0]
                    [6,0,4,1,0,2]
                    [0,0,6,0,3,4]
                ],
                box_shape=(3, 2),
            )
        >>> print(sudoku)
         --------------------
        ┆ 1  2 │    4 │    5 ┆
        ┆ 4  6 │      │ 2    ┆
        ┆      │    6 │ 4  1 ┆
        ┆──────┼──────┼──────┆
        ┆    4 │ 5  3 │      ┆
        ┆ 6    │ 4  1 │    2 ┆
        ┆      │ 6    │ 3  4 ┆
         --------------------
        """
        self.checkBoxShapeValid(
            box_shape,
            box_shape_name="initialization argument box_shape",
        )
        self._box_shape = box_shape
        self.checkBoardFormatValid(
            initial_board,
            board_side_length=self.board_side_length,
            board_name="initialization argument initial_board",
        )
        self._initial_board = tuple(tuple(row) for row in initial_board)
        if self.checkBoardForImmediateConflicts(initial_board, self.box_shape):
            raise ValueError("The Sudoku board represented by initialization argument initial_board contains a direct conflict")

    @staticmethod
    def checkBoxShapeValid(
        box_shape_prov: Any,
        box_shape_name: str="box shape",
    ) -> None:
        """
        Static method to check whether a value given for the attribute
        box_shape (representing the dimensions of the boxes in the
        Sudoku grid) is valid. An invalid value results in an exception
        being raised.

        A value for box_shape is valid if and only if it is an
        iterable indexable container (e.g. a list or tuple) with exactly
        two elements, both being strictly positive ints.

        Args:
            box_shape_prov (Any): Proposed box_shape value to be
                    checked for validity.
            box_shape_name (str, optional): The name given to the
                    proposed box_shape value in any potential error
                    message.

        Returns:
        None

        Raises:
            TypeError: Raised if the proposed box_shape value is not an
                    indexable container or any of its elements are not
                    integer types
            ValueError: Raised if box_shape does not contain exactly two
                    elements or either of its elements are not strictly
                    positive.
        """
        if not hasattr(box_shape_prov, "__getitem__"):
            raise TypeError(f"{box_shape_name} must an indexable container")
        box_shape_prov2 = tuple(box_shape_prov)
        if len(box_shape_prov2) != 2:
            raise ValueError(f"{box_shape_name} must have exactly two elements")
        elif not all(isinstance(x, int) for x in box_shape_prov2):
            raise TypeError(f"Each element of {box_shape_name} must be an integer")
        elif any(x <= 0 for x in box_shape_prov2):
            raise ValueError(f"Every element of {box_shape_name} must be strictly positive")
        return

    @property
    def box_shape(self) -> tuple[int, int]:
        """
        Read-only property

        tuple[int, int]: 2-tuple of strictly positive ints representing
        the box shape of the Sudoku, with index 0 containing
        the number of rows of the grid in each box and index 1
        containing the number of columns of the grid in each box.
        """
        return self._box_shape

    @property
    def board_side_length(self) -> int:
        """
        Read-only property

        int: Strictly positive integer representing the number of rows
        and columns in the Sudoku board (which we refer to as the side
        length). This is derived from the attribute box_shape, being the
        product of the two values in that attribute.
        """
        if getattr(self, "_board_shape", None) is None:
            self._board_side_length = self.box_shape[0] * self.box_shape[1]
        return self._board_side_length

    @staticmethod
    def checkBoardFormatValid(
        board_prov: Any,
        board_side_length: int,
        board_name: str,
    ) -> None:
        """
        Static method to check whether a value given for the attribute
        board (representing the values in the Sudoku board) is of a
        valid format, given a (presumed valid) side length of the Sudoku
        board board_side_length. An invalid value results in an exception
        being raised.

        A value for board is for a given strictly positive integer
        board_side_length has a valid format if and only if it satisfies
        every one of the following properties:
         1) board is an indexable container (e.g. a list or tuple)
            with a defined length equal to board_side_length
         2) every element of board is also an indexable container
            with a defined length equal to board_side_length
         3) every element inside every container inside board is
            an integer between 0 and board_side_length inclusive.

        Note that this only checks the format of the board. It does not
        check whether the Sudoku is solvable or even whether there are
        immediate conflicts between set values (the latter of which
        can be checked instead by the method
        checkBoardForImmediateConflicts()).

        Args:
            board_prov (Any): Proposed board value to be checked for
                    validity.
            board_side_length (int): Strictly positive integer giving
                    the required side length (i.e. the number of rows
                    and columns) of the Sudoku board that board_prov
                    is intended to represent.
            board_name (str, optional): The name given to the proposed
                    board value in any potential error message.

        Returns:
        None

        Raises:
            TypeError: Raised if the proposed board value (board_prov)
                    is not an indexable container with defined length
                    or any of its elements are not indexable containers
                    with defined length containing only integers
            ValueError: Raised if the length of board or the length of
                    any of its elements is not equal to board_side_length
                    or any of the containers in board holds an integer
                    that is not between 0 and board_side_length inclusive.
        """
        if not hasattr(board_prov, "__getitem__") or not hasattr(board_prov, "__len__"):
            raise TypeError(f"{board_name} must be an indexable container with defined length.")
        if len(board_prov) != board_side_length:
            raise ValueError(f"{board_name} must have length {board_side_length}")
        for i in range(len(board_prov)):
            try:
                row = board_prov[i]
            except IndexError:
                raise TypeError(f"{board_name} must be an indexable container with defined length.")
            if not hasattr(row, "__getitem__") or not hasattr(row, "__len__"):
                raise TypeError(f"every row of {board_name} must be an indexable container with defined length.")
            if len(row) != board_side_length:
                raise ValueError(f"every row in {board_name} must have length {board_side_length}")
            for j in range(len(row)):
                try:
                    num = row[j]
                except IndexError:
                    raise TypeError(f"every row in {board_name} must be an indexable container with defined length.")
                
                if not isinstance(num, int):
                    raise TypeError(f"every entry in {board_name} must be an integer")
                if num > board_side_length or num < 0:
                    raise ValueError(f"every entry in {board_name} must be an integer between 0 and {board_side_length} inclusive.")
        return
    
    @property
    def initial_board(self) -> tuple[tuple[int, ...], ...]:
        """
        Read-only property

        tuple[tuple[int, ...], ...]: Tuple of tuples of ints representing
        the values in the initial Sudoku board (as given on initialization).
        The outer tuple and each inner tuple have length equal to the
        attribute board_side_length, with the inner tuples representing the
        initial Sudoku board rows in order from top to bottom, and each
        integer representing the Sudoku board elements in that row from
        left to right, with elements that are initially set (i.e. the
        values that are given at the beginning of the puzzle) equal to that
        set value and elements that are not initially set (i.e. the values
        that are to be determined when solving the puzzle) equal to 0.
        """
        return self._initial_board

    @staticmethod
    def checkBoardForImmediateConflicts(
        board: list[list[int]],
        box_shape: tuple[int, int],
    ) -> bool:
        """
        Static method determining whether a Sudoku board with
        a given box shape contains any immediate conflicts
        (i.e. there is a row, column or box that contains
        more than one of the same set number).

        Note that a returned value of False does not guarantee
        that the Sudoku board has a solution (though a returned
        value of True guarantees that the Sudoku board does
        not have a solution).

        Args:
            board (list[list[int]]): A list of lists of
                    integers, representing the Sudoku board to be
                    checked for immediate conflicts, where
                    each inner list represents a row of the Sudoku
                    board. The outer list and each of the inner lists
                    must have the same number of elements as the side
                    length of the Sudoku grid (equal to the product of
                    the two box_shape dimensions, by default 9), and each
                    element of the inner list must be an integer between
                    0 and the side length of the Sudoku grid inclusive,
                    with the elements with set initial values given by
                    that strictly positive integer value and the
                    initially unset elements represented by the value
                    zero.
                    It is assumed that the format of board is valid
                    for the given box shape (i.e. the length of the
                    lists and the values in the inner lists obey the
                    conditions given above), and this will not be
                    checked.
            box_shape (tuple[int, int]): 2-tuple of strictly
                    positive integers specifying the shape of the
                    Sudoku boxes of the Sudoku represented by board,
                    where index 0 and 1 represent the number of rows
                    and columns respectively of the grid that appear
                    in each box.

        Returns:
            bool: Boolean specifying whether for the given Sudoku
                    box shape, the Sudoku represented by board
                    contains any immediate conflicts, True indicating
                    that at least one such conflict was identified
                    and False indicating that no such conflicts were
                    identified.
        """
        board_side_length = box_shape[0] * box_shape[1]
        for row in board:
            seen = set()
            for num in row:
                if not num: continue
                if num in seen:
                    #print(1, (i1, i2))
                    return True
                seen.add(num)
        for i2 in range(board_side_length):
            seen = set()
            for row in board:
                if not row[i2]: continue
                if row[i2] in seen:
                    return True
                seen.add(row[i2])
        for i1_0 in range(0, board_side_length, box_shape[0]):
            for i2_0 in range(0, board_side_length, box_shape[1]):
                seen = set()
                for i1 in range(i1_0, i1_0 + box_shape[0]):
                    for i2 in range(i2_0, i2_0 + box_shape[1]):
                        if not board[i1][i2]:
                            continue
                        if board[i1][i2] in seen:
                            return True
                        seen.add(board[i1][i2])
        return False
    
    def checkSolutionValid(
        self,
        board: list[list[int]],
    ) -> bool:
        """
        Identifies whether a given Sudoku board represents a solution
        to this Sudoku.

        A Sudoku board is a valid solution to this Sudoku if and only
        if every one of the following conditions are true:
         1) It is a valid format for a Sudoku board (so represents a 
             square grid of integers containing non-negative values no
             greater than the side length of the board).
         2) It has side length equal to the attribute board_side_length
             (and so the same dimensions as the Sudoku represented by
             this object).
         3) Every element is set (i.e. has no zero values and the
             Sudoku is completed).
         4) The board has no immediate conflicts for the box dimensions
             of this Sudoku (so no row, column or box contains the same
             number more than once).

        Args:
            board (list[list[int]]): A list of lists of integers,
                    representing the Sudoku board to be checked as to
                    whether it is a solution to this Sudoku.

        Returns:
            bool: True if board represents a valid solution to the
                    Sudoku represented by this object, otherwise False.
        """
        
        try:
            self.checkBoardFormatValid(
                board,
                self.board_side_length,
                "proposed solution",
            )
        except (ValueError, TypeError, IndexError):
            return False
        num_mx = self.board_side_length
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                if self.initial_board[i1][i2] and board[i1][i2] != self.initial_board[i1][i2]:
                    return False
        return not self.checkBoardForImmediateConflicts(board, self.box_shape)

    @staticmethod
    def getBoardPrintString(
        board: list[list[int]],
        box_shape: tuple[int, int],
        initial_numbers_bold: bool=False,
        initial_board: Optional[list[list[int]]]=None,
        check_box_shape_and_board_validity: bool=True,
    ) -> str:
        """
        Static method creating a string representing a given Sudoku with
        formatting (including aligning columns, adding a border, adding
        dividing lines between boxes and the option of the numbers set in
        the initial Sudoku board being marked in bold), intended for use
        in printing to console. Unset elements are left as an empty space.

        Examples of the type of formatting produced when printing to
        console are given in the Examples section (note that bold cannot
        be demonstrated here).

        Args:
            board (list[list[int]]): A list of lists of integers,
                    representing the values in the Sudoku board on which
                    the returned string is to be based, where the value
                    0 is used to denote an element that is not set 
                    (represented in the string as an empty space).
            box_shape (tuple[int, int]): 2-tuple of strictly
                    positive integers specifying the shape of the
                    Sudoku boxes of the Sudoku represented by board,
                    where index 0 and 1 represent the number of rows
                    and columns respectively of the grid that appear
                    in each box.
            initial_numbers_bold (bool, optional): If True, then the
                    initially set elements of board (as identified by
                    if given, the argument initial_board) are marked as
                    bold in the returned string, if False then none of
                    the elements are marked as bold.
                Default: False
            initial_board (Optional[list[list[int]]], optional): If given,
                    a list of lists of integers, representing the values
                    in the initial Sudoku board which the argument board
                    is based (i.e. with the same dimensions but with all,
                    none or some of the unset entries in initial_board
                    being set in board). This is only used in the case that
                    the argument initial_numbers_bold to identify the
                    initially set elements. If not given (or given as None),
                    none of the elements are marked in bold in the returned
                    string regardless of the argument initial_numbers_bold.
                Default: None
            check_box_shape_and_board_validity (bool, optional): If True,
                    then the arguments box_shape and board checked as to
                    the validity of their format and their are consistent
                    with each other, with an invalid result giving rise
                    to the appropriate exception being raised. If False, then
                    this check is skipped (this option being available
                    so as to avoid unnecessarily checking already checked
                    or known valid inputs).
                Default: True

        Returns:
            str: String representing the given Sudoku board with formatting,
                    suitable for printing to console.
        """

        if check_box_shape_and_board_validity:
            Sudoku.checkBoxShapeValid(box_shape, box_shape_name="box shape")
            board_side_len = box_shape[0] * box_shape[1]
            Sudoku.checkBoardFormatValid(
                board,
                board_side_length=board_side_len,
                board_name="board",
            )
            if initial_numbers_bold and initial_board is not None:
                Sudoku.checkBoardFormatValid(
                    initial_board,
                    board_side_length=board_side_len,
                    board_name="initial board",
                )
        else:
            board_side_len = box_shape[0] * box_shape[1]

        
        max_n_dig = len(str(board_side_len))

        def getNumString(num: int, is_bold: bool=False) -> str:
            if not num:
                return " " * max_n_dig
            s0 = str(num)
            length = len(s0)
            if is_bold:
                s0 = "".join(["\033[1m", s0, "\033[0;0m"])
            diff = max_n_dig - length
            r_pad = diff >> 1
            l_pad = r_pad + (diff & 1)
            return f"{' ' * l_pad}{s0}{' ' * r_pad}"
        end_row = " " + "-" * ((max_n_dig + 2) * board_side_len + box_shape[0] - 1)
        mid_row = "".join(["┆", "┼".join(["─" * ((box_shape[1] * (max_n_dig + 2)) + 0)] * box_shape[0]), "┆"])
        row_lst = [end_row]

        is_bold = (lambda i1, i2: False) if initial_board is None or not initial_numbers_bold else (lambda i1, i2 : bool(initial_board[i1][i2]))

        def addLayerString(i0: int) -> None:
            for i in range(i0, i0 + box_shape[0]):
                s_lst = ["┆ "]
                for j0 in range(0, board_side_len, box_shape[1]):
                    s_lst.append("  ".join([f"{getNumString(board[i][j], is_bold=is_bold(i, j))}" for j in range(j0, j0 + box_shape[1])]))
                    s_lst.append(" │ ")
                s_lst.pop()
                s_lst.append(" ┆")
                row_lst.append("".join(s_lst))
            return

        for i0 in range(0, board_side_len - box_shape[0], box_shape[0]):
            addLayerString(i0)
            row_lst.append(mid_row)
        addLayerString(board_side_len - box_shape[0])
        row_lst.append(end_row)
        return "\n".join(row_lst)

    def getInitialBoardPrintString(
        self,
        initial_numbers_bold: bool=False,
    ) -> None:
        """
        Creates a string representing the initial board of this Sudoku
        with formatting (including aligning columns, adding a border,
        adding dividing lines between boxes and the option of the numbers
        set in the initial Sudoku board being marked in bold), intended
        for use in printing to console. Unset elements are left as an
        empty space.

        For examples of the appearance of the formatted string when
        printed to console, see the documentation of the static method
        getBoardPrintString().

        Args:
            initial_numbers_bold (bool, optional): If True, then the
                    initially set elements of board (in this case,
                    all set elements) are marked as bold in the returned
                    string, if False then none of the elements are marked
                    as bold.
                Default: False

        Returns:
            str: String representing the given initial board of this Sudoku
                    with formatting suitable for printing to console.
        """
        return self.getBoardPrintString(
            self.initial_board,
            self.box_shape,
            initial_numbers_bold=initial_numbers_bold,
            initial_board=self.initial_board,
            check_box_shape_and_board_validity=False,
        )

    def __str__(self) -> str:
        """
        Returns a formatted string representing the initial Sudoku
        board represented by this object.
        """
        return self.getInitialBoardPrintString(initial_numbers_bold=True)

    @classmethod
    def loadSudokuFromCSV(cls, filename_in: str) -> Sudoku:
        """
        Class method for loading a Sudoku from a .csv file as a
        Sudoku object.
        
        The contents of a .csv file representing a Sudoku should
        be as follows:
          Line 1: A pair of comma separated strictly positive integers
                giving the box shape of the Sudoku (the number of rows
                and columns respectively in each box).
          Subsequent lines: Comma separated non-negative integer values,
                the lines giving the rows of the initial Sudoku board
                in order from top to bottom and each line containing the
                values in the corresponding Sudoku row from left to
                right in order, with the unset elements represented
                by 0. The number of subsequent lines and the number
                of comma separated values in each of these lines must
                equal the product of the two elements on line 1, with
                no integer value in these lines exceeding this product.
        Empty lines are ignored and lines whose first non-space
        character is "#" are treated as comments and are so also
        ignored.

        Args:
            filename_in (str): Relative or absolute path to the .csv
                    file from which the Sudoku is to be loaded.

        Raises:
            TypeError: Raised if filename_in is not a string or any
                    of the comma separated values in filename_in are
                    not integers.
            FileNotFoundError: Raised if filename_in does not correspond
                    to a file.
            ValueError: Raised if the .csv file at filename_in is not
                    a .csv file, the data in that .csv file is not
                    in the format described above or the Sudoku board
                    represented by the .csv files contains immediate
                    conflicts (i.e. more than one of the same set
                    value in a row, column or box).

        Returns:
            Sudoku: Sudoku object representing the Sudoku stored in the
                    .csv file at filename_in.
        
        Example:
        
        A .csv file containing the data:
        >>> # Easy standard Sudoku
            3,3
            7,8,0,4,0,0,1,2,0
            6,0,0,0,7,5,0,0,9
            0,0,0,6,0,1,0,7,8
            0,0,7,0,4,0,2,6,0
            0,0,1,0,5,0,9,3,0
            9,0,4,0,6,0,0,0,5
            0,7,0,3,0,0,0,1,2
            1,2,0,0,0,7,4,0,0
            0,4,9,2,0,6,0,0,7
        
        corresponds to the initial Sudoku board:
        >>>  -----------------------------
            ┆ 8       │         │         ┆
            ┆       3 │ 6       │         ┆
            ┆    7    │    9    │ 2       ┆
            ┆─────────┼─────────┼─────────┆
            ┆    5    │       7 │         ┆
            ┆         │    4  5 │ 7       ┆
            ┆         │ 1       │    3    ┆
            ┆─────────┼─────────┼─────────┆
            ┆       1 │         │    6  8 ┆
            ┆       8 │ 5       │    1    ┆
            ┆    9    │         │ 4       ┆
             -----------------------------
        """
        if not isinstance(filename_in, str):
            raise TypeError("filename_in must be a string")
        filename_in = filename_in.strip()
        if not filename_in.endswith(".csv"):
            raise ValueError("filename_in must be the path to a .csv file")
        abs_path = os.path.abspath(filename_in)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"no file found at {filename_in} (absolute path {abs_path})")
        box_shape = ()
        board = []
        with open(abs_path) as file:
            reader = csv.reader(file)
            it = iter(reader)
            for row in it:
                if not row or (row[0].lstrip() and row[0].lstrip()[0] == "#"): continue
                if len(row) != 2:
                    raise ValueError(
                        "the first non-empty row of a CSV file containing a Sudoku "
                        "must consist of exactly two strictly positive integers "
                        "separated by a comma")
                box_shape = tuple(int(num_str.strip()) for num_str in row)
                break
            for row in it:
                if not row or (row[0].lstrip() and row[0].lstrip() == "#"): continue
                board.append([int(num_str.strip()) for num_str in row])
        return Sudoku(board, box_shape)
    
    def encodePosition(self, pos: tuple[int, int]) -> int:
        """
        Finds the standardised encoding as a single integer of the
        position of an element of the Sudoku board as a single
        non-negative integer strictly less than the attribute
        board_side_length squared.

        For a given element of a Sudoku board, the position
        of the element is a 2-tuple of non-negative integers, both
        strictly less than the side length of the Sudoku board, where
        index 0 specifies the 0-indexed row of the element (with the
        top row taking index 0 and all other rows having an index
        exactly one greater than the row directly above) and index 1
        specifies the 0-indexed column of the element (with the
        leftmost column taking index 0 and all other columns having
        and index exactly one greater than the column directly to
        its left).

        The standardised encoding maps each valid position on the
        Sudoku board onto an integer distinct from that of every
        other valid position, with each non-negative integer strictly
        less than board_side_length squared equal to the encoding of
        exactly one valid position on the Sudoku board. This enables
        unambiguous decoding (performed by the method decodePostion()).

        Args:
            pos (tuple[int, int]): 2-tuple of non-negative integers,
                    both strictly less than board_side_length, giving
                    the position on the Sudoku board to be encoded.

        Raises:
            ValueError: Raised if either element of pos is negative
                    or is greater than or equal to the attribute
                    board_side_length.

        Returns:
            int: The standardised encoding of the element of the
                    Sudoku board with position pos.
        """
        for idx in pos:
            if idx < 0 or idx >= self.board_side_length:
                raise ValueError("Both elements of pos must be between "
                            f"0 and {self.board_side_length - 1} inclusive")
        return pos[0] * self.board_side_length + pos[1]
    
    def decodePosition(self, pos_enc: int) -> tuple[int, int]:
        """
        Finds the position of the element of the Sudoku board whose
        standardised encoding is the non-negative integer enc_idx.

        For more information regarding the position of an element on
        the Sudoku board and the standardised encoding, see the
        documentation of the method encodePosition().

        Args:
            pos_enc (int): Non-negative integer strictly less than
                    the attribute board_side_length squared giving the
                    standardised encoding of the element of the Sudoku
                    whose position is to be returned.
        
        Raises:
            ValueError: Raised if enc_pos is negative or is greater
                    than or equal to the attribute board_side_length
                    squared.
                    
        Returns:
            tuple[int, int]: 2-tuple of non-negative integers giving
                    the position of the element of the Sudoku board
                    whose standardised encoding in enc_pos.
        """
        if pos_enc < 0 or pos_enc >= self.board_side_length ** 2:
            raise ValueError("pos_enc must be between 0 and "
                            f"{self.board_side_length ** 2 - 1} includisve")
        return divmod(pos_enc, self.board_side_length)

    def createInitialStateVariables(
        self,
    ) -> tuple[np.ndarray, SortedDict, np.ndarray, np.ndarray]:
        """
        Creates the initial state variables for this Sudoku:
         1) The bitmask state array- an array of bitmasks representing
            the potential (non-excluded) values available to each
            element of the Sudoku board.
         2) The element options count dictionary, a sorted dictionary
            grouping the encoded positions of elements that have not
            yet been set (i.e. have more than one potential value) by
            the number of potential values they each have available.
         3) The region available values bitmask array, which for each
            region (i.e. each row, column and box in the Sudoku grid)
            uses a bitmask to represent the values that have not yet
            been set in that region.
         4) The region available spaces bitmask array, which for each
            region (i.e. each row, column and box in the Sudoku grid)
            uses a bitmask to represent the positions of the elements
            in that region that have not yet been set (i.e. have more
            than one potential value).

        These are calculated for the initial Sudoku board (the attribute
        initial_board), calculating the four variables taking into
        account the initially set values, but performing no simplification
        of the board (i.e. no logic is performed to calculate any of
        the consequences, even obvious ones, on any other element of
        the grid beyond excluding values used by other elements in
        any of the shared regions from the potential values available).

        Returns:
            tuple[np.ndarray, SortedDict, np.ndarray, np.ndarray]:

                Index 0 (np.ndarray): The bitmask state array, a
                    2-dimensional square numpy array of unsigned ints
                    (np.uint) with side length equal to the attribute
                    board_side_length, where the integers correspond
                    to a bitmask, where the 0-indexed i:th bit is set
                    (i.e. the (i + 1):th rightmost bit in the binary
                    representation of the bitmask integer is 1) if and
                    only if the value (i + 1) has not been excluded as
                    a potential value the corresponding element of the
                    Sudoku might take.

                Index 1 (SortedDict): The element options count dictionary,
                    a sorted dictionary whose keys are integers strictly
                    greater than 1, representing the number of non-excluded
                    values each Sudoku element with more than one such
                    non-excluded values have, with the corresponding value
                    being a set of integers comprising the encoded positions
                    in the Sudoku board that have that number of non-excluded
                    values.

                Index 2 (np.ndarray): The region available values bitmask
                    array, a 2-dimensional numpy array of unsigned
                    ints (np.uint) with dimension 0 of length 3 and
                    dimension 1 of length equal to the
                    attribute board_side_length. The element with index
                    (idx1, idx2) gives a bitmask representing the values
                    not yet set in the region of type idx1 (where 0 is
                    a row, 1 is a column, 2 is a box), with region index
                    idx2, where a number i is not one of the set values
                    in that region if and only if the (i - 1):th bit in
                    the bitmask is set (i.e. the i:th rightmost digit
                    in the binary representation of the bitmask integer
                    is 1).

                Index 3 (np.ndarray): The regiona available spaces bitmask
                    array, a 2-dimensional numpy array of unsigned ints
                    (np.uint) with dimension 0 of length 3 and dimension 1
                    of length equal to the attribute board_side_length.
                    The element with index (idx1, idx2) gives a bitmask
                    signifying which of the elements in the region of type
                    idx1 (where 0 is a row, 1 is a column, 2 is a box) with
                    region index idx2 that have not yet been set to a value
                    (i.e. have more than one potential value). For an
                    element in this region whose index within that region
                    is i, that element's value has not yet been set to a
                    value if and only if the (i - 1):th bit in the bitmask
                    is set (i.e. the i:th rightmost digit in the binary
                    representation of the bitmask integer is 1).
        """
        num_mx = self.board_side_length
        dtype = np.uint
        if num_mx <= 16:
            dtype = np.uint16
        elif num_mx <= 32:
            dtype = np.uint32
        elif num_mx <= 64:
            dtype = np.uint64
        #elif num_mx <= 128:
        #    dtype = np.uint128
        #elif num_mx <= 256:
        #    dtype = np.uint256
        else:
            dtype = object
            #raise ValueError("Sudoku too large to solve (only accepts sudoku side length no greater than 64)")
        opts_count_dict = SortedDict()
        z_val = (1 << num_mx) - 1
        
        curr_state_bm = np.full(shape=(self.board_side_length, self.board_side_length), fill_value=z_val, dtype=dtype)
        region_available_nums_bm = np.full(shape=(3, self.board_side_length), fill_value=z_val, dtype=dtype)
        region_available_spaces_bm = np.full(shape=(3, self.board_side_length), fill_value=z_val, dtype=dtype)
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                if self.initial_board[i1][i2]:
                    num_bm = dtype(1 << (self.initial_board[i1][i2] - 1))
                    num_bm_complement = ~num_bm
                    curr_state_bm[i1, i2] = num_bm
                    region_inds_lst = self.getRegionIndicesFromPosition((i1, i2))
                    #num_bm_complement = dtype(~(1 << self.initial_board[i1, i2]))
                    for region_typ_idx, region_inds in enumerate(region_inds_lst):
                        region_available_nums_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(
                            region_available_nums_bm[region_typ_idx, region_inds[0]],
                            num_bm_complement,
                        )
                        region_available_spaces_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(
                            region_available_spaces_bm[region_typ_idx, region_inds[0]],
                            ~dtype(1 << region_inds[1]),
                        )
                    #unset_opts[0, 0, row_idx] -= 
                    #n_set += 1
                    continue
                opts_count_dict.setdefault(num_mx, set())
                opts_count_dict[num_mx].add(np.ubyte(self.encodePosition((i1, i2))))
        return (curr_state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm)
    
    @staticmethod
    def getLeastSignificantSetBit(bm: np.uint) -> np.uint:
        """
        Static method calculated for an unsigned integer the index
        of the smallest set bit (i.e. the smallest power of 2 whose
        corresponding bit in the binary representation of the
        unsigned integer is 1).

        Args:
            bm (np.uint): Unsigned integer for which the index of
                    the least significant set bit is to be calculated.

        Returns:
            np.uint: The least significant set bit of the unsigned integer
                    bm.
        """
        return np.frexp(bm & (~(bm - 1)))[1] - 1
    
    @staticmethod
    def bitmaskComponentsGenerator(
        bm: np.uint,
    ) -> Generator[np.uint, None, None]:
        """
        Generator iterating over the components of the
        bitmask unsigned integer bm in order of increasing
        size.
        
        A component of a bitmask is a power of 2 whose
        corresponding bit in the binary representation of
        the bitmask unsigned integer is 1.

        Args:
            bm (np.uint): Unsigned integer representing the
                    bitmask whose components are to be
                    iterated over.

        Yields:
            np.uint: A component of the bitmask bm. Collectively,
                    every component of bm is yielded exactly
                    once and are yielded in order of strictly
                    increasing size.
        """
        while bm:
            bm2 = np.bitwise_and(bm, ~(bm - 1))
            yield bm2
            bm ^= bm2
        return

    @staticmethod
    def bitmaskIndicesGenerator(
        bm: np.uint,
    ) -> Generator[np.uint, None, None]:
        """
        Generator iterating over the 0-indexed indices
        of the components of the bitmask unsigned integer
        bm in order of increasing size.
        
        A component of a bitmask is a power of 2 whose
        corresponding bit in the binary representation of
        the bitmask unsigned integer is 1. The index of
        this component is the logarithm base 2 of component
        (i.e. the exponent of 2 equal to the component).

        Args:
            bm (np.uint): Unsigned integer representing the
                    bitmask whose component indices are to be
                    iterated over.

        Yields:
            np.uint: The index of a component of the bitmask bm.
                    Collectively, the index of every component
                    of bm is yielded exactly once and are yielded
                    in order of strictly increasing size.
        """
        while bm:
            bm2 = np.bitwise_and(bm, ~(bm - 1))
            yield np.frexp(bm2)[1] - 1
            bm ^= bm2
        return

    def stateArray2Board(
        self,
        state_bm: np.ndarray,
    ) -> list[list[int]]:
        """
        Converts a bitmask state array into the corresponding
        Sudoku. For elements with more than one option, the
        returned board takes the value 0, signifying that the
        element is unset.
        
        A bitmask state array for a given Sudoku is a 2-dimensional
        array with the same dimensions as the initial Sudoku board
        (or equivalently is a square array with side length equal
        to the attribute board_side_length for that Sudoku object),
        whose elements are bitmasks representing the values that
        the element may take. A given element may take a given value
        num if and only if the bit with zero-indexed index (num - 1)
        of the bitmask of that element is set (i.e. the bit num from
        the right of the binary representation of the bitmask integer
        has the value 1). Consequently, a given element in the
        bitmask state array has a set value if and only if the
        bitmask of that element has exactly one set bit (of equivalently
        the bitmask integer is equal to a non-negative power of 2).
        Given that for a given Sudoku no value greater than its value
        of board_side_length is allowed, the bitmask integer of any
        element in the bitmask state array must be strictly less than
        2 ** board_side_length.

        Args:
            state_bm (np.ndarray): 2-dimensional square numpy array
                    of np.uint:s, whose side length is equal to the
                    attribute board_side_length

        Returns:
            list[list[int]]: The Sudoku board corresponding to the
                    given bitmask state array for this Sudoku.
        """
        num_mx = self.board_side_length
        res = [[0] * num_mx for _ in range(num_mx)]
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                bm = state_bm[i1][i2]
                if not bm: return []
                res[i1][i2] = 0 if np.bitwise_count(bm) > 1 else int(self.getLeastSignificantSetBit(bm)) + 1
        return res

    def getRowSlice(self, row_idx: int) -> tuple[slice, slice]:
        """
        Calculates the slice of the Sudoku board corresponding
        to the Sudoku row with 0-indexed index row_idx.

        Args:
            row_idx (int): Non-negative integer giving the
                    0-indexed index of the row for which the
                    slice is to be found.

        Raises:
            ValueError: Raised if row_idx is not non-negative or
                    is not strictly less than the attribute
                    board_side_length.
                    
        Returns:
            tuple[slice, slice]: 2-tuple of slice objects, with
                    index 0 corresponding to the range of 0-indexed
                    rows of the Sudoku board and 1 corresponding to
                    the range of 0-indexed columns of the Sudoku
                    board comprising the row with 0-indexed index
                    row_idx.
        """
        if not 0 <= row_idx < self.board_side_length:
            raise ValueError("row_idx must be between 0 and "
                            f"{self.board_side_length - 1} inclusive")
        return (slice(row_idx, row_idx + 1), slice(None))
    
    def getColumnSlice(self, col_idx: int) -> tuple[slice, slice]:
        """
        Calculates the slice of the Sudoku board corresponding
        to the Sudoku column with 0-indexed index col_idx.

        Args:
            col_idx (int): Non-negative integer giving the
                    0-indexed index of the column for which the
                    slice is to be found.

        Raises:
            ValueError: Raised if col_idx is not non-negative or
                    is not strictly less than the attribute
                    board_side_length.
                    
        Returns:
            tuple[slice, slice]: 2-tuple of slice objects, with
                    index 0 corresponding to the range of 0-indexed
                    rows of the Sudoku board and 1 corresponding to
                    the range of 0-indexed columns of the Sudoku
                    board comprising the column with 0-indexed index
                    col_idx.
        """
        if not 0 <= col_idx < self.board_side_length:
            raise ValueError("col_idx must be between 0 and "
                            f"{self.board_side_length - 1} inclusive")
        return (slice(None), slice(col_idx, col_idx + 1))
    
    def getBoxSlice(self, box_idx: int) -> tuple[slice, slice]:
        """
        Calculates the slice of the Sudoku board corresponding
        to the Sudoku box with 0-indexed index box_idx.

        Args:
            box_idx (int): Non-negative integer giving the
                    0-indexed index of the box for which the
                    slice is to be found.

        Raises:
            ValueError: Raised if box_idx is not non-negative or
                    is not strictly less than the attribute
                    board_side_length.
                    
        Returns:
            tuple[slice, slice]: 2-tuple of slice objects, with
                    index 0 corresponding to the range of 0-indexed
                    rows of the Sudoku board and 1 corresponding to
                    the range of 0-indexed columns of the Sudoku
                    board comprising the box with 0-indexed index
                    box_idx.
        """
        if not 0 <= box_idx < self.board_side_length:
            raise ValueError("box_idx must be between 0 and "
                            f"{self.board_side_length - 1} inclusive")
        j1, j2 = divmod(box_idx, self.box_shape[0])
        #print(j1, j2)
        return (
            slice(self.box_shape[0] * j1, self.box_shape[0] * (j1 + 1)),
            slice(self.box_shape[1] * j2, self.box_shape[1] * (j2 + 1)),
        )

    def getSlice(
        self,
        region_typ_idx: int,
        region_ext_idx: int,
    ) -> tuple[slice, slice]:
        """
        Calculates the slice of the Sudoku board corresponding
        to the Sudoku region (i.e. row, column or box) with 0-indexed
        region type index region_typ_idx and 0-indexed index for
        the regions of that type region_ext_idx.

        The region type indices correspond to the following region types:
            0- corresponds to row regions
            1- corresponds to column regions
            2- corresponds to box regions

        Args:
            region_typ_idx (int): Integer between 0 and 2 inclusive
                    indicating the type of region the slice should
                    represent, with 0 corresponding to row, 1 to
                    column and 2 to box.
            region_ext_idx (int): Non-negative integer giving the
                    0-indexed index of the region for which the
                    slice is to be found.

        Raises:
            ValueError: Raised if region_ext_idx is not non-negative
                    or is not strictly less than the attribute
                    board_side_length, or if region_typ_idx is not
                    between 0 and 2 inclusive.
                    
        Returns:
            tuple[slice, slice]: 2-tuple of slice objects, with
                    index 0 corresponding to the range of 0-indexed
                    rows of the Sudoku board and 1 corresponding to
                    the range of 0-indexed columns of the Sudoku
                    board comprising the region with 0-indexed region
                    type region_typ_idx and 0-indexed index of the
                    region of that type region_ext_idx.
        """
        if not 0 <= region_ext_idx < self.board_side_length:
            raise ValueError("region_ext_idx must be between 0 and "
                            f"{self.board_side_length - 1} inclusive")
        match region_typ_idx:
            case 0:
                res = self.getRowSlice(region_ext_idx)
            case 1:
                res = self.getColumnSlice(region_ext_idx)
            case 2:
                res = self.getBoxSlice(region_ext_idx)
            case _:
                raise ValueError("slc_typ must be an integer between 0 and 2 inclusive")
        return res
    
    def regionIndices2Position(
        self,
        region_typ_idx: int,
        region_inds: tuple[int, int],
    ) -> tuple[int, int]:
        """
        For a given Sudoku region type (row, column or box based on
        region_typ_idx), converts the region indices of an element
        of the Sudoku board to its position.

        For a given element of a Sudoku board, the region indices of
        the element with respect to a given region type (row, column
        or box) is a 2-tuple of non-negative integers, both strictly
        less than the side length of the Sudoku board, with the index 0
        specifying (0-indexed) the standardised index of the region of
        the given region type containing the element, and index 1
        specifying the (0-indexed) standardised index of that element
        with respect to that region.

        For a given element of a Sudoku board, the position
        of the element is a 2-tuple of non-negative integers, both
        strictly less than the side length of the Sudoku board, where
        index 0 specifies the 0-indexed row of the element (with the
        top row taking index 0 and all other rows having an index
        exactly one greater than the row directly above) and index 1
        specifies the 0-indexed column of the element (with the
        leftmost column taking index 0 and all other columns having
        and index exactly one greater than the column directly to
        its left).

        Args:
            region_typ_idx (int): Integer between 0 and 2 inclusive
                    indicating the type of region the slice should
                    represent, with 0 corresponding to row, 1 to
                    column and 2 to box.
            region_inds (tuple[int, int]): 2-tuple of non-negative
                    integers, both strictly less than the attribute
                    box_side_length, giving the region indices of the
                    element whose position is to be returned.

        Raises:
            ValueError: Raised if either element of region_inds is
                    negative or is greater than or equal to the
                    attribute box_side_length.

        Returns:
            tuple[int, int]: 2-tuple of non-negative integers
                    strictly less than the attribute box_side_length
                    giving the position of the element of the Sudoku
                    board whose region indices with respect to the
                    region type corresponding to region_typ_idx
                    are region_inds.
        """
        for region_idx in region_inds:
            if not 0 <= region_idx < self.board_side_length:
                raise ValueError("Both elements of region_inds must be between "
                                f"0 and {self.board_side_length - 1} inclusive")
        match region_typ_idx:
            case 0:
                # Row
                res = tuple(region_inds)
            case 1:
                # Column
                res = tuple(region_inds[::-1])
            case 2:
                # Box
                box_ext_inds = divmod(region_inds[0], self.box_shape[0])
                box_int_inds = divmod(region_inds[1], self.box_shape[1])
                res = tuple(x * y + z for x, y, z in zip(box_ext_inds, self.box_shape, box_int_inds))
            case _:
                raise ValueError("slc_typ must be an integer between 0 and 2 inclusive")
        return res
    
    def regionIndices2EncodedPosition(
        self,
        region_typ_idx: int,
        region_inds: tuple[int, int],
    ) -> int:
        """
        For a given Sudoku region type (row, column or box based on
        region_typ_idx), converts the region indices of to encoded
        position.

        For a given element of a Sudoku board, the region indices of
        the element with respect to a given region type (row, column
        or box) is a 2-tuple of non-negative integers, both strictly
        less than the side length of the Sudoku board, with the index 0
        specifying (0-indexed) the standardised index of the region of
        the given region type containing the element, and index 1
        specifying the (0-indexed) standardised index of that element
        with respect to that region.

        For a given element of a Sudoku board, the position
        of the element is a 2-tuple of non-negative integers, both
        strictly less than the side length of the Sudoku board, where
        index 0 specifies the 0-indexed row of the element (with the
        top row taking index 0 and all other rows having an index
        exactly one greater than the row directly above) and index 1
        specifies the 0-indexed column of the element (with the
        leftmost column taking index 0 and all other columns having
        and index exactly one greater than the column directly to
        its left).
        The encoded position for a given element is calculated
        by uniquely encoding the position to a non-negative integer
        that is strictly less than the attribute board_side_length
        squared using the method encodePosition().

        Args:
            region_typ_idx (int): Integer between 0 and 2 inclusive
                    indicating the type of region the slice should
                    represent, with 0 corresponding to row, 1 to
                    column and 2 to box.
            region_inds (tuple[int, int]): 2-tuple of non-negative
                    integers, both strictly less than the attribute
                    box_side_length, giving the region indices of the
                    element whose encoded position is to be
                    returned.

        Raises:
            ValueError: Raised if either element of region_inds is
                    negative or is greater than or equal to the
                    attribute box_side_length.

        Returns:
            int: Non-negative integer strictly less than the square
                    of box_side_length giving the encoded position
                    of the element of the Sudoku board whose region
                    indices with respect to the region type
                    corresponding to region_typ_idx are region_inds.
        """
        return self.encodePosition(
            self.regionIndices2Position(region_typ_idx, region_inds)
        )

    def getRegionIndicesFromPosition(
        self,
        pos: tuple[int, int],
    ) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        """
        For each Sudoku region type (row, column and box), calculates
        the region indices of the element of the Sudoku board at
        position pos. These are returned in order row, column, box
        region indices.

        For a given element of a Sudoku board, the position
        of the element is a 2-tuple of non-negative integers, both
        strictly less than the side length of the Sudoku board, where
        index 0 specifies the 0-indexed row of the element (with the
        top row taking index 0 and all other rows having an index
        exactly one greater than the row directly above) and index 1
        specifies the 0-indexed column of the element (with the
        leftmost column taking index 0 and all other columns having
        and index exactly one greater than the column directly to
        its left).

        For a given element of a Sudoku board, the region indices of
        the element with respect to a given region type (row, column
        or box) is a 2-tuple of non-negative integers, both strictly
        less than the side length of the Sudoku board, with the index 0
        specifying (0-indexed) the standardised index of the region of
        the given region type containing the element, and index 1
        specifying the (0-indexed) standardised index of that element
        with respect to that region.

        Args:
            pos (tuple[int, int]): 2-tuple of non-negative integers,
                    both strictly less than board_side_length, giving
                    the position on the Sudoku board whose region
                    indices for the different region types are to
                    be calculated.

        Raises:
            ValueError: Raised if either element of pos is negative
                    or is greater than or equal to the attribute
                    board_side_length.

        Returns:
            tuple[tuple[int, int], tuple[int, int], tuple[int, int]]: 3-tuple
                    of 2-tuples of non-negative integers strictly less than
                    board_side_length, with each 2-tuple giving the region
                    indices of the Sudoku board element at position pos for
                    a different region type, with the 2-tuple index to
                    region type correspondence being:
                      0- row
                      1- column
                      2- box
        """
        for idx in pos:
            if not 0 <= idx < self.board_side_length:
                raise ValueError("Both elements of pos must be between 0 and "
                                f"{self.board_side_length - 1} inclusive")
        i1, j1 = divmod(pos[0], self.box_shape[0])
        i2, j2 = divmod(pos[1], self.box_shape[1])

        #box_idx = (idx1 // self.box_shape[0]) * self.box_shape[0] + (idx2 // self.box_shape[1])
        return ((pos[0], pos[1]), (pos[1], pos[0]), (i1 * self.box_shape[0] + i2, j1 * self.box_shape[1] + j2))

    def getRegionIndicesFromEncodedPosition(
        self,
        pos_enc: int,
    ) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        """
        For each Sudoku region type (row, column and box), calculates
        the region indices of the element of the Sudoku board with
        encoded position pos_enc. These are returned in order row,
        column, box region indices.

        For a given element of a Sudoku board, the position
        of the element is a 2-tuple of non-negative integers, both
        strictly less than the side length of the Sudoku board, where
        index 0 specifies the 0-indexed row of the element (with the
        top row taking index 0 and all other rows having an index
        exactly one greater than the row directly above) and index 1
        specifies the 0-indexed column of the element (with the
        leftmost column taking index 0 and all other columns having
        and index exactly one greater than the column directly to
        its left).
        The encoded position for a given element is calculated
        by uniquely encoding the position to a non-negative integer
        that is strictly less than the attribute board_side_length
        squared using the method encodePosition().

        For a given element of a Sudoku board, the region indices of
        the element with respect to a given region type (row, column
        or box) is a 2-tuple of non-negative integers, both strictly
        less than the side length of the Sudoku board, with the index 0
        specifying (0-indexed) the standardised index of the region of
        the given region type containing the element, and index 1
        specifying the (0-indexed) standardised index of that element
        with respect to that region.

        Args:
            pos_enc (int): Non-negative integer strictly less than
                    the attribute board_side_length squared giving the
                    standardised encoding of the element of the Sudoku
                    board whose region indices for the different region
                    types are to be calculated.

        Raises:
            ValueError: Raised if pos_enc is negative or is greater than
                    or equal to board_side_length squared.

        Returns:
            tuple[tuple[int, int], tuple[int, int], tuple[int, int]]: 3-tuple
                    of 2-tuples of non-negative integers strictly less than
                    board_side_length, with each 2-tuple giving the region
                    indices of the Sudoku board element with encoded position
                    pos_enc for a different region type, with the 2-tuple
                    index to region type correspondence being:
                      0- row
                      1- column
                      2- box
        """
        return self.getRegionIndicesFromPosition(self.decodePosition(pos_enc))

    def simplifyState(
        self,
        state_bm: np.ndarray,
        opts_count_dict: SortedDict,
        region_available_nums_bm: np.ndarray,
        region_available_spaces_bm: np.ndarray,
        pos_enc_changed: set[int],
    ) -> bool:
        """
        For a given Sudoku board state following changes to
        given board elements, uses logic to iteratively simplify
        the board states by removing options that are now impossible
        and recognising when elements have only a single possible
        option. Additionally, recognises when a direct contradiction
        is identified (either a set of different numbers are forced
        to collectively inhabit a smaller number of spaces, or
        there is no place in a region of the Sudoku that can take
        a given value).

        At present, the simplifications take two forms:
         1) For Sudoku regions (rows, columns, boxes), identifies
            when a number is only an option for a single element
            in that region, thus forcing that element to take that
            number value.
         2) When a Sudoku board element has only one option as to its
            value, leading to that value being excluded as an option
            for any other element in the regions (i.e. the row, column
            and box) to which the element belongs.
        
        Note that the simplification takes the form of direct
        modification of the input arguments state_bm, opts_count_dict,
        region_available_nums_bm and/or region_available_spaces_bm.
        
        Increasing the scope of simplifications is a target for future
        optimisation, for example identifying naked and/or hidden
        pairs and triples.

        Args:
            state_bm (np.ndarray): 2-dimensional square numpy array
                    of unsigned ints (np.uint) with side length equal
                    to the attribute board_side_length, where the
                    integers correspond to a bitmask, where the
                    0-indexed i:th bit is set (i.e. the (i + 1):th
                    rightmost bit in the binary representation of the
                    bitmask integer is 1) if and only if the value
                    (i + 1) has not been excluded as a potential value
                    the corresponding element of the Sudoku might take.
            opts_count_dict (SortedDict): Sorted dictionary whose keys
                    are integers strictly greater than 1, representing
                    the number of non-excluded values the Sudoku elements
                    with more than one such non-excluded values have, with
                    the corresponding value being a set of integers
                    comprising the encoded positions that have that
                    number of non-excluded values.
            region_available_nums_bm (np.ndarray): 2-dimensional numpy
                    array of unsigned ints (np.uint) with dimension 0
                    of length 3 and dimension 1 of length equal to the
                    attribute board_side_length. The element with index
                    (idx1, idx2) gives a bitmask representing the values
                    not yet set in the region of type idx1 (where 0 is
                    a row, 1 is a column, 2 is a box), with region index
                    idx2, where a number i is not one of the set values
                    in that region if and only if the (i - 1):th bit in
                    the bitmask is set (i.e. the i:th rightmost digit
                    in the binary representation of the bitmask integer
                    is 1).
            region_available_spaces_bm (np.ndarray): 2-dimensional numpy
                    array of unsigned ints (np.uint) with dimension 0
                    of length 3 and dimension 1 of length equal to the
                    attribute board_side_length. The element with index
                    (idx1, idx2) gives a bitmask signifying which of the
                    elements in the region of type idx1 (where 0 is a row,
                    1 is a column, 2 is a box) with region index idx2 that
                    have not yet been set to a value (i.e. have more than one
                    potential value). For an element in this region whose
                    index within that region is i, that element's value has
                    not yet been set to a value if and only if the
                    (i - 1):th bit in the bitmask is set (i.e. the i:th
                    rightmost digit in the binary representation of the
                    bitmask integer is 1).
            pos_enc_changed (set[int]): Set of integers representing the
                    encoded positions whose bitmasks in state_bm have
                    been altered since the previous application of this
                    method (or, for the first use of this method, the
                    encoded positions of the initially set elements).

        Returns:
            bool: True if no direct contradiction has been identified in
                    the Sudoku during the simplification, False otherwise.
        """
        dtype = state_bm.dtype.type
        if dtype == object: dtype = int

        num_mx = self.board_side_length
        pos_enc_in_stk = set(pos_enc_changed)
        pos_enc_stk = list(pos_enc_changed)
        while pos_enc_stk:
            enc_idx = pos_enc_stk.pop()
            pos_enc_in_stk.remove(enc_idx)
            
            pos = self.decodePosition(enc_idx)
            
            region_inds_lst = self.getRegionIndicesFromPosition(pos)
            bm0 = state_bm[*pos]
            chk_bm0 = dtype((1 << num_mx) - 1) ^ bm0
            
            # Checking for elements that share a region with the changed element that
            # are now the only potential representative of a given digit
            for region_typ_idx, region_inds in enumerate(region_inds_lst):
                slc = self.getSlice(region_typ_idx, region_inds[0])
                slc_arr = np.ravel(state_bm[*slc], order="C")
                region_int_idx = region_inds[1]
                chk_bm = np.bitwise_and(chk_bm0, region_available_nums_bm[region_typ_idx, region_inds[0]])
                for bm2 in slc_arr:
                    if np.bitwise_count(bm2) == 1:
                        chk_bm = np.bitwise_and(chk_bm, ~bm2)
                for bm2 in self.bitmaskComponentsGenerator(chk_bm):
                    slc_idx_lst = np.where(np.bitwise_and(slc_arr, bm2))[0]
                    if len(slc_idx_lst) != 1: continue
                    inds2 = self.regionIndices2Position(region_typ_idx, (region_inds[0], slc_idx_lst[0]))
                    enc_idx2 = self.encodePosition(inds2)
                    opts_cnt = np.bitwise_count(state_bm[*inds2])
                    if opts_cnt <= 1:
                        return False
                    state_bm[*inds2] = bm2
                    opts_count_dict[opts_cnt].remove(enc_idx2)
                    if not opts_count_dict[opts_cnt]: opts_count_dict.pop(opts_cnt)
                    if enc_idx2 in pos_enc_in_stk: continue
                    pos_enc_in_stk.add(enc_idx2)
                    pos_enc_stk.append(enc_idx2)
            
            if np.bitwise_count(bm0) != 1: continue

            # The changed element has only one option
            bm0_compl = ~bm0
            for region_typ_idx, region_inds in enumerate(region_inds_lst):
                slc = self.getSlice(region_typ_idx, region_inds[0])
                slc_arr = np.ravel(state_bm[*slc], order="C")
                region_int_idx_set = set(np.where(np.bitwise_and(slc_arr, bm0))[0]) - {region_inds[1]}
                for region_int_idx in region_int_idx_set:
                    inds2 = self.regionIndices2Position(region_typ_idx, (region_inds[0], region_int_idx))
                    enc_idx2 = self.encodePosition(inds2)
                    opts_cnt = np.bitwise_count(state_bm[*inds2])
                    if opts_cnt == 1: return False
                    state_bm[*inds2] = np.bitwise_and(state_bm[*inds2], ~bm0)
                    opts_count_dict[opts_cnt].remove(enc_idx2)
                    if not opts_count_dict[opts_cnt]: opts_count_dict.pop(opts_cnt)
                    opts_cnt2 = opts_cnt - 1
                    if opts_cnt2 > 1:
                        opts_count_dict.setdefault(opts_cnt2, set())
                        opts_count_dict[opts_cnt2].add(enc_idx2)
                    if enc_idx2 in pos_enc_in_stk: continue
                    pos_enc_in_stk.add(enc_idx2)
                    pos_enc_stk.append(enc_idx2)
                region_available_nums_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(
                    region_available_nums_bm[region_typ_idx, region_inds[0]],
                    bm0_compl,
                )
                region_available_spaces_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(
                    region_available_spaces_bm[region_typ_idx, region_inds[0]],
                    ~dtype(1 << region_inds[1]),
                )
        return True

    def solutionsGenerator(
        self,
    ) -> Generator[list[list[int]], None, None]:
        """
        Generator iterating over every possible valid solution
        of the Sudoku.

        Yields:
            list[list[int]]: List of lists of integers representing
                    one of the solutions of the Sudoku board, where
                    the outer list and each of the inner lists has
                    length equal to the attribute board_side_length,
                    each list in the outer list represents a row
                    of the Sudoku board (ordered from top to bottom)
                    and each element in an inner list is a strictly
                    positive integer no greater than the attribute
                    board_side_length that represents the value of
                    an element in that row (ordered from left to
                    right) the corresponding Sudoku board element
                    takes for the solution being yielded.
                    The solutions are yielded in the order they
                    are identified by the backtracking algorithm
                    used to find the solutions, meaning there
                    is no particular significance to the order
                    the solutions are yielded in terms of their
                    contents.
        
        Example:
        >>> sudoku = Sudoku(
        ...     [
        ...         [7, 8, 0, 4, 0, 0, 1, 2, 0],
        ...         [6, 0, 0, 0, 7, 5, 0, 0, 9],
        ...         [0, 0, 0, 6, 0, 1, 0, 7, 8],
        ...         [0, 0, 7, 0, 4, 0, 2, 6, 0],
        ...         [0, 0, 1, 0, 5, 0, 9, 3, 0],
        ...         [9, 0, 4, 0, 6, 0, 0, 0, 5],
        ...         [0, 7, 0, 3, 0, 0, 0, 1, 2],
        ...         [1, 2, 0, 0, 0, 7, 4, 0, 0],
        ...         [0, 4, 9, 2, 0, 6, 0, 0, 7],
        ...     ]
        ... )
        >>> print(sudoku)
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
        >>> for sol in sudoku.solutionsGenerator():
        ...     print(
        ...         sudoku.getBoardPrintString(
        ...             sol,
        ...             sudoku.box_shape,
        ...             initial_numbers_bold=False,
        ...             initial_board=sudoku.initial_board,
        ...             check_box_shape_and_board_validity=False,
        ...         )
        ...     )
         -----------------------------
        ┆ 7  8  5 │ 4  3  9 │ 1  2  6 ┆
        ┆ 6  1  2 │ 8  7  5 │ 3  4  9 ┆
        ┆ 4  9  3 │ 6  2  1 │ 5  7  8 ┆
        ┆─────────┼─────────┼─────────┆
        ┆ 8  5  7 │ 9  4  3 │ 2  6  1 ┆
        ┆ 2  6  1 │ 7  5  8 │ 9  3  4 ┆
        ┆ 9  3  4 │ 1  6  2 │ 7  8  5 ┆
        ┆─────────┼─────────┼─────────┆
        ┆ 5  7  8 │ 3  9  4 │ 6  1  2 ┆
        ┆ 1  2  6 │ 5  8  7 │ 4  9  3 ┆
        ┆ 3  4  9 │ 2  1  6 │ 8  5  7 ┆
         -----------------------------
        
        """
        state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm = self.createInitialStateVariables()
        pos_enc_changed = set(range(self.board_side_length * self.board_side_length))
        for pos_enc in opts_count_dict.values():
            pos_enc_changed -= pos_enc
        self.simplifyState(
            state_bm,
            opts_count_dict,
            region_available_nums_bm,
            region_available_spaces_bm,
            pos_enc_changed,
        )

        def recur(
            state_bm: np.ndarray,
            opts_count_dict: SortedDict,
            region_available_nums_bm: np.ndarray,
            region_available_spaces_bm: np.ndarray,
        ) -> Generator[list[list[list[int]]], None, None]:
            if not opts_count_dict:
                yield self.stateArray2Board(state_bm)
                return
            
            dtype = state_bm.dtype.type
            if dtype == object: dtype = int
            
            n_opts, pos_enc = opts_count_dict.peekitem(0)
            enc_idx = next(iter(pos_enc))
            pos = self.decodePosition(enc_idx)
            for j in self.bitmaskIndicesGenerator(state_bm[*pos]):
                state_bm2 = copy.deepcopy(state_bm)
                num_bm = dtype(1 << j)
                num_bm_compl = ~num_bm
                state_bm2[*pos] = num_bm
                opts_count_dict2 = SortedDict({x: set(y) for x, y in opts_count_dict.items()})
                opts_count_dict2[n_opts].remove(enc_idx)
                region_inds_lst = self.getRegionIndicesFromPosition(pos)
                region_available_nums_bm2 = copy.deepcopy(region_available_nums_bm)
                region_available_spaces_bm2 = copy.deepcopy(region_available_spaces_bm)
                for region_typ_idx, region_inds in enumerate(region_inds_lst):
                    region_available_nums_bm2[region_typ_idx, region_inds[0]] = np.bitwise_and(
                        region_available_nums_bm2[region_typ_idx, region_inds[0]],
                        num_bm_compl,
                    )
                    region_available_spaces_bm2[region_typ_idx, region_inds[0]] = np.bitwise_and(
                        region_available_spaces_bm2[region_typ_idx, region_inds[0]],
                        ~dtype(1 << region_inds[1]),
                    )
                if not opts_count_dict2[n_opts]: opts_count_dict2.pop(n_opts)
                if self.simplifyState(
                    state_bm2,
                    opts_count_dict2,
                    region_available_nums_bm2,
                    region_available_spaces_bm2,
                    {enc_idx},
                ):
                    yield from recur(
                        state_bm2,
                        opts_count_dict2,
                        region_available_nums_bm2,
                        region_available_spaces_bm2,
                    )
            return

        yield from recur(
            state_bm,
            opts_count_dict,
            region_available_nums_bm,
            region_available_spaces_bm,
        )
        return

class InvalidSudokuSolution(Exception):
    """
    Exception raised when an invalid solution to a given
    Sudoku if put forward as a solution. This can be
    for reasons including:
     1) The dimensions of the Sudoku do not match the
        initial Sudoku board.
     2) The solution has unset entries (so has not been
        completed).
     3) Elements that were set in the initial Sudoku take
        a different value in the solution
     4) The solution contains immediate conflicts (i.e.
        the same value appears more than once in a row,
        column or box of the Sudoku).
    """

def findAllSolutionsToSudokuInCSV(
    filename_in: str,
    check_solution_valid: bool=True,
    raise_error_if_invalid_found: bool=True,
    initial_numbers_bold=True,
) -> tuple[str, list[str]]:
    """
    For a Sudoku stored in a .csv file at filename_in,
    returns a formatted string representing that Sudoku
    and a similarly formatted string representing every
    possible solution of that Sudoku.

    The contents of a .csv file representing a Sudoku should
        be as follows:
          Line 1: A pair of comma separated strictly positive integers
                giving the box shape of the Sudoku (the number of rows
                and columns respectively in each box).
          Subsequent lines: Comma separated non-negative integer values,
                the lines giving the rows of the initial Sudoku board
                in order from top to bottom and each line containing the
                values in the corresponding Sudoku row from left to
                right in order, with the unset elements represented
                by 0. The number of subsequent lines and the number
                of comma separated values in each of these lines must
                equal the product of the two elements on line 1, with
                no integer value in these lines exceeding this product.
        Empty lines are ignored and lines whose first non-space
        character is "#" are treated as comments and are so also
        ignored.

    Args:
        filename_in (str): Relative or absolute path to the .csv
                    file from which the Sudoku to be solved is loacated.
        check_solution_valid (bool, optional): If given as True, checks
                each solution found to ensure it is a valid solution
                to the Sudoku. Otherwise, it is assumed that
                each solution found is valid.
            Default: True
        raise_error_if_invalid_found (bool, optional): If given as True,
                in the case that a solution is identified that when
                checked is not a valid solution to this Sudoku, an
                InvalidSudokuSolution is raised. Otherwise, this
                invalid solution is simply ignored and not included in
                the returned list of solutions.
            Default: True
        initial_numbers_bold (bool, optional): If given as True, the
                returned Sudoku strings (including the initial Sudoku)
                will mark the numbers initially et in the Sudoku (i.e.
                the non-zero numbers in the .csv file) to be formatted
                in bold, with the others not marked as bold. Otherwise,
                none of the numbers in the returned Sudoku strings are
                marked as bold.
            Default: True

    Raises:
        InvalidSudokuSolution: Raised if check_solution_valid and
                raise_error_if_invalid_found are both given as True
                and one of the solutions, when checked is found not
                to be a valid solution.

    Returns:
        tuple[str, list[str]]:
            Index 0: String representing the Sudoku stored in filename_in
                in its initial state (i.e. before starting the solve).
                This string is formatted for printing to console.

            Index 1: List of strings representing all solutions to the
                Sudoku stored in filename_in. Each string represents
                a completed solution to this Sudoku (i.e. all of the
                entries in the Sudoku are set in a manner consistent
                with the Sudoku rules for a Sudoku of the given box
                size), formatted for printing to console.
                In the case that there is more than one solution,
                there is no special significance to the order these
                appear in this list.
    """
    sudoku = Sudoku.loadSudokuFromCSV(filename_in)
    res = [sudoku.getInitialBoardPrintString(initial_numbers_bold=initial_numbers_bold), []]
    for sol in sudoku.solutionsGenerator():
        sol_str = sudoku.getBoardPrintString(
            sol,
            sudoku.box_shape,
            initial_numbers_bold=initial_numbers_bold,
            initial_board=sudoku.initial_board,
            check_box_shape_and_board_validity=False,
        )
        if check_solution_valid and not sudoku.checkSolutionValid(sol):
            if raise_error_if_invalid_found:
                raise InvalidSudokuSolution(f"invalid solution returned:\n{sol_str}")
            continue
        res[1].append(sol_str)
    return tuple(res)

def findAnySolutionToSudokuInCSV(
    filename_in: str,
    check_solution_valid: bool=True,
    raise_error_if_invalid_found: bool=True,
    initial_numbers_bold=True,
) -> tuple[str, Optional[str]]:
    """
    For a Sudoku stored in a .csv file at filename_in,
    returns a formatted string representing that Sudoku
    and a similarly formatted string representing one
    possible solution to the Sudoku (if such a solution
    exists).

    The contents of a .csv file representing a Sudoku should
        be as follows:
          Line 1: A pair of comma separated strictly positive integers
                giving the box shape of the Sudoku (the number of rows
                and columns respectively in each box).
          Subsequent lines: Comma separated non-negative integer values,
                the lines giving the rows of the initial Sudoku board
                in order from top to bottom and each line containing the
                values in the corresponding Sudoku row from left to
                right in order, with the unset elements represented
                by 0. The number of subsequent lines and the number
                of comma separated values in each of these lines must
                equal the product of the two elements on line 1, with
                no integer value in these lines exceeding this product.
        Empty lines are ignored and lines whose first non-space
        character is "#" are treated as comments and are so also
        ignored.

    Args:
        filename_in (str): Relative or absolute path to the .csv
                    file from which the Sudoku to be solved is loacated.
        check_solution_valid (bool, optional): If given as True, checks
                the solution found (if any) to ensure it is a valid
                solution to the Sudoku. Otherwise, it is assumed that
                it is a valid solution.
            Default: True
        raise_error_if_invalid_found (bool, optional): If given as True,
                in the case that a solution is identified that when
                checked is not a valid solution to this Sudoku, an
                InvalidSudokuSolution is raised. Otherwise, this
                invalid solution is simply ignored and the first solution
                found to be valid (if any) is given as the solution.
            Default: True
        initial_numbers_bold (bool, optional): If given as True, the
                returned Sudoku strings (including the initial Sudoku)
                will mark the numbers initially et in the Sudoku (i.e.
                the non-zero numbers in the .csv file) to be formatted
                in bold, with the others not marked as bold. Otherwise,
                none of the numbers in the returned Sudoku strings are
                marked as bold.
            Default: True

    Raises:
        InvalidSudokuSolution: Raised if check_solution_valid and
                raise_error_if_invalid_found are both given as True
                and one of the solutions, when checked is found not
                to be a valid solution.

    Returns:
        tuple[str, Optional[str]]:
            Index 0: String representing the Sudoku stored in filename_in
                in its initial state (i.e. before starting the solve).
                This string is formatted for printing to console.

            Index 1: If a solution is found, a string representing
                that solution to the Sudoku stored in filename_in,
                otherwise None. The string represents the completed
                solution to this Sudoku found (i.e. all of the entries
                in the Sudoku are set in a manner consistent with the
                Sudoku rules for a Sudoku of the given box size),
                formatted for printing to console.
    """
    sudoku = Sudoku.loadSudokuFromCSV(filename_in)
    res = [sudoku.getInitialBoardPrintString(initial_numbers_bold=initial_numbers_bold), None]
    for sol in sudoku.solutionsGenerator():
        sol_str = sudoku.getBoardPrintString(
            sol,
            sudoku.box_shape,
            initial_numbers_bold=initial_numbers_bold,
            initial_board=sudoku.initial_board,
            check_box_shape_and_board_validity=False,
        )
        if check_solution_valid and not sudoku.checkSolutionValid(sol):
            if raise_error_if_invalid_found:
                raise InvalidSudokuSolution(f"invalid solution returned:\n{sol_str}")
            continue
        res[1] = sol_str
        break
    return tuple(res)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="SudokuSolver",
        description=(
            "Program solving Sudokus stored in .csv files, printing "
            "a solution or the solutions (if any) to console."
        )
    )

    parser.add_argument(
        "filename",
        help="The path to the .csv file containing the Sudoku to be solved",
    )
    parser.add_argument(
        "-s",
        "--single",
        action="store_true",
        help=(
            "If this flag is used, specifies that only one of the possible"
            "solutions (if any exist) should be found and printed, with "
            "the search stopped after a solution is found. Otherwise all "
            "possible solutions to the Sudoku are to be found and printed."
        ),
    )

    args = parser.parse_args()
    filename_in : str = args.filename
    single_solution : bool = args.single

    initial_numbers_bold : bool = True

    since = time.time()
    if single_solution:
        try:
            init_str, sol_str = findAnySolutionToSudokuInCSV(
                filename_in,
                check_solution_valid=True,
                raise_error_if_invalid_found=True,
                initial_numbers_bold=initial_numbers_bold,
            )
        except InvalidSudokuSolution as e:
            sys.exit(str(e))
        print("Initial Sudoku:")
        print(init_str)
        if sol_str is None:
            print("No solutions found")
        else:
            print(f"Solution")
            print(sol_str)
            print(f"total search time before finding a solution = {(time.time() - since):.4f} seconds")
        return
    try:
        init_str, sol_strs = findAllSolutionsToSudokuInCSV(
            filename_in,
            check_solution_valid=True,
            raise_error_if_invalid_found=True,
            initial_numbers_bold=initial_numbers_bold,
        )
    except InvalidSudokuSolution as e:
        sys.exit(str(e))
    print("Initial Sudoku:")
    print(init_str)
    sol_cnt = 0
    for sol_str in sol_strs:
        sol_cnt += 1
        print(f"Solution {sol_cnt}")
        print(sol_str)
    t = (time.time() - since)
    pl_str = "" if sol_cnt == 1 else "s"
    print(f"\nThis Sudoku has exactly {sol_cnt} solution{pl_str}")
    print(f"time to search for all possible solutions = {t:.4f} seconds")
    return

if __name__ == "__main__":
    main()