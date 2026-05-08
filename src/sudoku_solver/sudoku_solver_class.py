
from __future__ import annotations

from typing import (
    Any,
    Generator,
)

import copy
import csv
import os
import sys
import time

#from collections import deque
import numpy as np
from sortedcontainers import SortedDict


class Sudoku(object):
    """
    Class whose instances represent specific Sudoku puzzles
    with boxes of arbitrary dimensions, including a method
    to find all possible solutions (if any) to the represented
    Sudoku.

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
                    or the componenets of its components are not
                    of the correct type (indexable, indexable and
                    integer types respectively) or box_shape or
                    its components are not of the correct type
                    (indexable or integer types respectively)/
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

        A value for board_prov is for a given strictly positive integer
        board_side_length has a valid format if and only if TODO

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
            TODO
            TypeError: Raised if the proposed box_shape value is not an
                    indexable container or any of its elements are not
                    integer types
            ValueError: Raised if box_shape does not contain exactly two
                    elements or either of its elements are not strictly
                    positive.
        """
        if len(board_prov) != board_side_length:
            raise ValueError(f"{board_name} must have length {board_side_length}")
        if any(len(row) != board_side_length for row in board_prov):
            raise ValueError(f"every row in {board_name} must have length {board_side_length}")
        if any(not isinstance(x, int) for row in board_prov for x in row):
            raise TypeError(f"every entry in {board_name} must be an integer")
        if any(x > board_side_length or x < 0 for row in board_prov for x in row):
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
    
    def _createIndexArray(self) -> np.ndarray:
        enc_idx_arr = np.zeros((self.board_side_length, self.board_side_length), dtype=np.ubyte)
        for i1 in range(self.board_side_length):
            for i2 in range(self.board_side_length):
                enc_idx_arr[i1, i2] = self.encodeIndices(i1, i2)
        return enc_idx_arr

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
            board (list[list[int]]): TODO

                    It is assumed that the format of board is
                    valid for the given box shape.
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
        ***HERE***

        Args:
            board (list[list[int]]): _description_

        Returns:
            bool: _description_
        """
        num_mx = self.board_side_length
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                if not isinstance(board[i1][i2], int) or board[i1][i2] < 1 or board[i1][i2] > num_mx:
                    return False
                elif self.initial_board[i1][i2] and board[i1][i2] != self.initial_board[i1][i2]:
                    return False
        return not self.checkBoardForImmediateConflicts(board, self.box_shape)

    def getBoardPrintString(
        self,
        board: list[list[int]],
        box_shape: tuple[int, int],
        initial_numbers_bold: bool=False,
    ) -> str:
        
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

        def addLayerString(i0: int) -> None:
            for i in range(i0, i0 + box_shape[0]):
                s_lst = ["┆ "]
                for j0 in range(0, board_side_len, box_shape[1]):
                    is_bold = lambda j : initial_numbers_bold and self.initial_board[i][j]
                    s_lst.append("  ".join([f"{getNumString(board[i][j], is_bold=is_bold(j))}" for j in range(j0, j0 + box_shape[1])]))
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

    def getInitialBoardPrintString(self, initial_numbers_bold: bool=False) -> None:
        return self.getBoardPrintString(self.initial_board, self.box_shape, initial_numbers_bold=initial_numbers_bold)

    def __str__(self) -> str:
        return self.getInitialBoardPrintString(initial_numbers_bold=True)

    @classmethod
    def loadSudokuFromCSV(cls, filename_in: str) -> Sudoku:
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
                    raise ValueError("the first non-empty row of a CSV file containing a sudoku must consist of exactly two strictly positive integers separated by a comma")
                box_shape = tuple(int(num_str.strip()) for num_str in row)
                break
            for row in it:
                if not row or (row[0].lstrip() and row[0].lstrip() == "#"): continue
                board.append([int(num_str.strip()) for num_str in row])
        return Sudoku(board, box_shape)
    
    def encodeIndices(self, idx1: int, idx2: int) -> int:
        return idx1 * self.board_side_length + idx2
    
    def decodeIndices(self, enc_idx: int) -> tuple[int, int]:
        return divmod(enc_idx, self.board_side_length)

    def _createInitialStateArray(self) -> tuple[np.ndarray, SortedDict, np.ndarray, np.ndarray]:
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
                    region_inds_lst = self.getRegionIndicesFromPosition(i1, i2)
                    #num_bm_complement = dtype(~(1 << self.initial_board[i1, i2]))
                    for region_typ_idx, region_inds in enumerate(region_inds_lst):
                        region_available_nums_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(region_available_nums_bm[region_typ_idx, region_inds[0]], num_bm_complement)
                        region_available_spaces_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(region_available_spaces_bm[region_typ_idx, region_inds[0]], ~dtype(1 << region_inds[1]))
                    #unset_opts[0, 0, row_idx] -= 
                    #n_set += 1
                    continue
                opts_count_dict.setdefault(num_mx, set())
                opts_count_dict[num_mx].add(np.ubyte(self.encodeIndices(i1, i2)))
        return (curr_state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm)
    
    @staticmethod
    def getSmallestSetBit(bm: np.uint) -> int:
        return np.frexp(bm & (~(bm - 1)))[1] - 1
    
    @staticmethod
    def bitmaskComponentsGenerator(bm: np.uint) -> Generator[int, None, None]:
        while bm:
            bm2 = np.bitwise_and(bm, ~(bm - 1))
            yield bm2
            bm ^= bm2
        return

    @staticmethod
    def bitmaskIndicesGenerator(bm: np.uint) -> Generator[int, None, None]:
        while bm:
            bm2 = np.bitwise_and(bm, ~(bm - 1))
            yield np.frexp(bm2)[1] - 1
            bm ^= bm2
        return

    def stateArray2Board(self, state_bm: np.ndarray) -> list[list[int]]:
        num_mx = self.board_side_length
        res = [[0] * num_mx for _ in range(num_mx)]
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                bm = state_bm[i1][i2]
                if not bm: return []
                res[i1][i2] = 0 if np.bitwise_count(bm) > 1 else int(self.getSmallestSetBit(bm)) + 1
        return res

    def getRowSlice(self, row_idx: int) -> tuple[slice, slice]:
        return (slice(row_idx, row_idx + 1), slice(None))
    
    def getColumnSlice(self, col_idx: int) -> tuple[slice, slice]:
        return (slice(None), slice(col_idx, col_idx + 1))
    
    def getBoxSlice(self, box_idx: int) -> tuple[slice, slice]:
        j1, j2 = divmod(box_idx, self.box_shape[0])
        #print(j1, j2)
        return (
            slice(self.box_shape[0] * j1, self.box_shape[0] * (j1 + 1)),
            slice(self.box_shape[1] * j2, self.box_shape[1] * (j2 + 1)),
        )

    def getSlice(self, region_typ_idx: int, region_ext_idx: int) -> tuple[slice, slice]:
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
    
    def regionIndices2Position(self, region_typ_idx: int, region_inds: tuple[int, int]) -> tuple[int, int]:
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
    
    def regionIndices2EncodedPosition(self, region_typ_idx: int, region_inds: tuple[int, int]) -> int:
        return self.encodeIndices(*self.regionIndices2Position(region_typ_idx, region_inds))

    def getRegionIndicesFromPosition(self, idx1: int, idx2: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        i1, j1 = divmod(idx1, self.box_shape[0])
        i2, j2 = divmod(idx2, self.box_shape[1])

        #box_idx = (idx1 // self.box_shape[0]) * self.box_shape[0] + (idx2 // self.box_shape[1])
        return ((idx1, idx2), (idx2, idx1), (i1 * self.box_shape[0] + i2, j1 * self.box_shape[1] + j2))

    def getRegionIndicesFromEncodedPosition(self, enc_idx: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        return self.getRegionIndicesFromPosition(*self.decodeIndices(enc_idx))

    def _simplifyState(
        self,
        state_bm: np.ndarray,
        opts_count_dict: SortedDict,
        region_available_nums_bm: np.ndarray,
        region_available_spaces_bm: np.ndarray,
        enc_inds_changed: set[int],
    ) -> bool:
        
        dtype = state_bm.dtype.type
        if dtype == object: dtype = int

        num_mx = self.board_side_length
        enc_inds_in_stk = set(enc_inds_changed)
        enc_inds_stk = list(enc_inds_changed)
        while enc_inds_stk:
            enc_idx = enc_inds_stk.pop()
            enc_inds_in_stk.remove(enc_idx)
            
            idx1, idx2 = self.decodeIndices(enc_idx)
            
            region_inds_lst = self.getRegionIndicesFromPosition(idx1, idx2)
            bm0 = state_bm[idx1, idx2]
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
                    enc_idx2 = self.encodeIndices(*inds2)
                    opts_cnt = np.bitwise_count(state_bm[*inds2])
                    if opts_cnt <= 1:
                        return False
                    state_bm[*inds2] = bm2
                    opts_count_dict[opts_cnt].remove(enc_idx2)
                    if not opts_count_dict[opts_cnt]: opts_count_dict.pop(opts_cnt)
                    if enc_idx2 in enc_inds_in_stk: continue
                    enc_inds_in_stk.add(enc_idx2)
                    enc_inds_stk.append(enc_idx2)
            
            if np.bitwise_count(bm0) != 1: continue

            # The changed element has only one option
            bm0_compl = ~bm0
            for region_typ_idx, region_inds in enumerate(region_inds_lst):
                slc = self.getSlice(region_typ_idx, region_inds[0])
                slc_arr = np.ravel(state_bm[*slc], order="C")
                region_int_idx_set = set(np.where(np.bitwise_and(slc_arr, bm0))[0]) - {region_inds[1]}
                for region_int_idx in region_int_idx_set:
                    inds2 = self.regionIndices2Position(region_typ_idx, (region_inds[0], region_int_idx))
                    enc_idx2 = self.encodeIndices(*inds2)
                    opts_cnt = np.bitwise_count(state_bm[*inds2])
                    if opts_cnt == 1: return False
                    state_bm[*inds2] = np.bitwise_and(state_bm[*inds2], ~bm0)
                    opts_count_dict[opts_cnt].remove(enc_idx2)
                    if not opts_count_dict[opts_cnt]: opts_count_dict.pop(opts_cnt)
                    opts_cnt2 = opts_cnt - 1
                    if opts_cnt2 > 1:
                        opts_count_dict.setdefault(opts_cnt2, set())
                        opts_count_dict[opts_cnt2].add(enc_idx2)
                    if enc_idx2 in enc_inds_in_stk: continue
                    enc_inds_in_stk.add(enc_idx2)
                    enc_inds_stk.append(enc_idx2)
                region_available_nums_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(region_available_nums_bm[region_typ_idx, region_inds[0]], bm0_compl)
                region_available_spaces_bm[region_typ_idx, region_inds[0]] = np.bitwise_and(region_available_spaces_bm[region_typ_idx, region_inds[0]], ~dtype(1 << region_inds[1]))
        return True

    

    def solutionsGenerator(self) -> Generator[list[list[int]], None, None]:
        state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm = self._createInitialStateArray()
        enc_inds_changed = set(range(self.board_side_length * self.board_side_length))
        for enc_inds in opts_count_dict.values():
            enc_inds_changed -= enc_inds
        self._simplifyState(state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm, enc_inds_changed)

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
            
            n_opts, enc_inds = opts_count_dict.peekitem(0)
            enc_idx = next(iter(enc_inds))
            idx1, idx2 = self.decodeIndices(enc_idx)
            for j in self.bitmaskIndicesGenerator(state_bm[idx1, idx2]):
                state_bm2 = copy.deepcopy(state_bm)
                num_bm = dtype(1 << j)
                num_bm_compl = ~num_bm
                state_bm2[idx1, idx2] = num_bm
                opts_count_dict2 = SortedDict({x: set(y) for x, y in opts_count_dict.items()})
                opts_count_dict2[n_opts].remove(enc_idx)
                region_inds_lst = self.getRegionIndicesFromPosition(idx1, idx2)
                region_available_nums_bm2 = copy.deepcopy(region_available_nums_bm)
                region_available_spaces_bm2 = copy.deepcopy(region_available_spaces_bm)
                for region_typ_idx, region_inds in enumerate(region_inds_lst):
                    region_available_nums_bm2[region_typ_idx, region_inds[0]] = np.bitwise_and(region_available_nums_bm2[region_typ_idx, region_inds[0]], num_bm_compl)
                    region_available_spaces_bm2[region_typ_idx, region_inds[0]] = np.bitwise_and(region_available_spaces_bm2[region_typ_idx, region_inds[0]], ~dtype(1 << region_inds[1]))
                if not opts_count_dict2[n_opts]: opts_count_dict2.pop(n_opts)
                if self._simplifyState(state_bm2, opts_count_dict2, region_available_nums_bm2, region_available_spaces_bm2, {enc_idx}):
                    yield from recur(state_bm2, opts_count_dict2, region_available_nums_bm2, region_available_spaces_bm2)
            return

        yield from recur(state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm)
        return

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Too few command line arguments")
    elif len(sys.argv) > 2:
        sys.exit("Too many command line arguments")
    filename = sys.argv[1]
    filename_in = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../sudoku_csv_files/{filename}"))
    sudoku = Sudoku.loadSudokuFromCSV(filename_in)
    print("Initial Sudoku:")
    print(sudoku)
    sol_cnt = 0
    since = time.time()
    for sol in sudoku.solutionsGenerator():
        sol_cnt += 1
        print(f"Solution {sol_cnt}")
        print(sudoku.getBoardPrintString(sol, sudoku.box_shape, initial_numbers_bold=True))
        print(f"solution is {'' if sudoku.checkSolutionValid(sol) else 'in'}valid")
        print(f"total search time before finding solution {sol_cnt} = {(time.time() - since):.4f} seconds")
    t = (time.time() - since)

    print(f"\ntotal number of solutions = {sol_cnt}")
    print(f"time to search for all possible solutions = {t:.4f} seconds")
    return

if __name__ == "__main__":
    main()