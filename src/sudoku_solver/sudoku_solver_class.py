
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
            initial_board (list[list[int]]): _description_
            box_shape (tuple[int, int], optional): _description_.
                
                Defaults to (3, 3)

        Raises:
            ValueError: Raised if the dimensions of 
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
        if self.checkBoardForImmediateConflicts(initial_board):
            raise ValueError("The Sudoku board represented by initialization argument initial_board contains a direct conflict")

    @staticmethod
    def checkBoxShapeValid(box_shape_prov: Any, box_shape_name: str) -> None:
        if len(box_shape_prov) != 2:
            raise ValueError(f"{box_shape_name} must have exactly two elements")
        elif not all(isinstance(x, int) for x in box_shape_prov):
            raise TypeError(f"Each element of {box_shape_name} must be an integer")
        elif any(x <= 0 for x in box_shape_prov):
            raise ValueError(f"Every element of {box_shape_name} must be strictly positive")
        return

    @property
    def box_shape(self) -> tuple[int, int]:
        return self._box_shape

    @property
    def board_side_length(self) -> int:
        if getattr(self, "_board_shape", None) is None:
            self._board_side_length = self.box_shape[0] * self.box_shape[1]
        return self._board_side_length

    @staticmethod
    def checkBoardFormatValid(board_prov: Any, board_side_length: int, board_name: str) -> None:
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
        return self._initial_board
    
    def _createIndexArray(self) -> np.ndarray:
        enc_idx_arr = np.zeros((self.board_side_length, self.board_side_length), dtype=np.ubyte)
        for i1 in range(self.board_side_length):
            for i2 in range(self.board_side_length):
                enc_idx_arr[i1, i2] = self.encodeIndices(i1, i2)
        return enc_idx_arr

    #@property
    #def enc_idx_arr(self) -> np.ndarray:
    #    if getattr(self, "_enc_idx_arr", None) is None:
    #        self._enc_idx_arr = self._createIndexArray()
    #    return self._enc_idx_arr

    def checkBoardForImmediateConflicts(self, board: list[list[int]]) -> bool:
        for row in board:
            seen = set()
            for num in row:
                if not num: continue
                if num in seen:
                    #print(1, (i1, i2))
                    return True
                seen.add(num)
        for i2 in range(self.board_side_length):
            seen = set()
            for row in board:
                if not row[i2]: continue
                if row[i2] in seen:
                    #print(2, (i1, i2))
                    return True
                seen.add(row[i2])
        for i1_0 in range(0, self.board_side_length, self.box_shape[0]):
            for i2_0 in range(0, self.board_side_length, self.box_shape[1]):
                seen = set()
                for i1 in range(i1_0, i1_0 + self.box_shape[0]):
                    for i2 in range(i2_0, i2_0 + self.box_shape[1]):
                        #print((i1, i2), seen)
                        if not board[i1][i2]:
                            continue
                        if board[i1][i2] in seen:
                            #print(3, (i1, i2))
                            return True
                        seen.add(board[i1][i2])
        return False
    
    def checkSolutionValid(self, board: list[list[int]]) -> bool:
        num_mx = self.board_side_length
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                if not isinstance(board[i1][i2], int) or board[i1][i2] < 1 or board[i1][i2] > num_mx:
                    return False
                elif self.initial_board[i1][i2] and board[i1][i2] != self.initial_board[i1][i2]:
                    return False
        return not self.checkBoardForImmediateConflicts(board)

    def getBoardPrintString(
        self,
        board: list[list[int]],
        box_shape: tuple[int, int],
        initial_numbers_bold: bool=False,
    ) -> str:
        base = 10
        
        board_side_len = box_shape[0] * box_shape[1]
        max_n_dig = len(str(board_side_len))
        #num = board_side_len

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
        #print(row_lst)
        return "\n".join(row_lst)

    def getInitialBoardPrintString(self, initial_numbers_bold: bool=False) -> None:
        return self.getBoardPrintString(self.initial_board, self.box_shape, initial_numbers_bold=initial_numbers_bold)

    def __str__(self) -> str:
        return self.getInitialBoardPrintString(initial_numbers_bold=True)

    #def printCurrentBoardToTerminal(self) -> None:
    #    pass

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
        #n_set = 0
        
        curr_state_bm = np.full(shape=(self.board_side_length, self.board_side_length), fill_value=z_val, dtype=dtype)
        #unset_opts = np.full(shape=(2, 3, self.board_side_length), fill_value=z_val, dtype=dtype)
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
        #print(bm)
        while bm:
            bm2 = np.bitwise_and(bm, ~(bm - 1))
            yield np.frexp(bm2)[1] - 1
            bm ^= bm2
        return

    def stateArray2Board(self, state_bm: np.ndarray) -> list[list[int]]:
        num_mx = self.board_side_length
        #print(state_bm)
        res = [[0] * num_mx for _ in range(num_mx)]
        for i1 in range(num_mx):
            for i2 in range(num_mx):
                bm = state_bm[i1][i2]
                if not bm: return []
                res[i1][i2] = 0 if np.bitwise_count(bm) > 1 else int(self.getSmallestSetBit(bm)) + 1
        #print(state_bm)
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
        #print(region_typ_idx, region_inds, res)
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

    def _simplifyState(self, state_bm: np.ndarray, opts_count_dict: SortedDict, region_available_nums_bm: np.ndarray, region_available_spaces_bm: np.ndarray, enc_inds_changed: set[int]) -> bool:
        
        dtype = state_bm.dtype.type
        if dtype == object: dtype = int

        num_mx = self.board_side_length
        enc_inds_in_stk = set(enc_inds_changed)
        enc_inds_stk = list(enc_inds_changed)
        while enc_inds_stk:
            enc_idx = enc_inds_stk.pop()
            enc_inds_in_stk.remove(enc_idx)
            
            idx1, idx2 = self.decodeIndices(enc_idx)
            
            #row_inds, col_inds, box_inds = self.getRegionIndicesFromPosition(idx1, idx2)
            region_inds_lst = self.getRegionIndicesFromPosition(idx1, idx2)
            bm0 = state_bm[idx1, idx2]
            chk_bm0 = dtype((1 << num_mx) - 1) ^ bm0
            
            # Checking for elements that share a region with the changed element that
            # are now the only potential representative of a given digit
            #for typ_idx, slc, ravel_idx in (("row", self.getRowSlice(row_inds[0]), row_inds[1]), ("column", self.getColumnSlice(col_inds[0]), col_inds[1]), ("box", self.getBoxSlice(box_inds[0]), box_inds[1])):
            for region_typ_idx, region_inds in enumerate(region_inds_lst):
                slc = self.getSlice(region_typ_idx, region_inds[0])
                slc_arr = np.ravel(state_bm[*slc], order="C")
                region_int_idx = region_inds[1]
                #slc_idx_arr = np.ravel(self.enc_idx_arr[*slc], order="C")
                chk_bm = chk_bm0
                for bm2 in slc_arr:
                    if np.bitwise_count(bm2) == 1:
                        chk_bm = np.bitwise_and(chk_bm, ~bm2)
                for bm2 in self.bitmaskComponentsGenerator(chk_bm):
                    slc_idx_lst = np.where(np.bitwise_and(slc_arr, bm2))[0]
                    if len(slc_idx_lst) != 1: continue
                    #enc_idx2 = slc_idx_arr[slc_idx_lst[0]]
                    inds2 = self.regionIndices2Position(region_typ_idx, (region_inds[0], slc_idx_lst[0]))
                    enc_idx2 = self.encodeIndices(*inds2)
                    #print(region_typ_idx, (region_inds[0], slc_idx_lst[0]), enc_idx2, enc_idx3)
                    #inds2 = self.decodeIndices(enc_idx2)
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
            #for slc in (self.getRowSlice(row_idx), self.getColumnSlice(col_idx), self.getBoxSlice(box_idx)):
            for region_typ_idx, region_inds in enumerate(region_inds_lst):
                slc = self.getSlice(region_typ_idx, region_inds[0])
                slc_arr = np.ravel(state_bm[*slc], order="C")
                #slc_idx_arr = np.ravel(self.enc_idx_arr[*slc], order="C")
                region_int_idx_set = set(np.where(np.bitwise_and(slc_arr, bm0))[0]) - {region_inds[1]}
                #enc_idx_set = set(slc_idx_arr[j] for j in slc_idx_lst) - {enc_idx}
                #enc_idx_set = set(self.regionIndices2EncodedPosition(region_typ_idx, (region_inds[0], slc_idx_set)))
                #for enc_idx2 in enc_idx_set:
                for region_int_idx in region_int_idx_set:
                    inds2 = self.regionIndices2Position(region_typ_idx, (region_inds[0], region_int_idx))
                    enc_idx2 = self.encodeIndices(*inds2)
                    #enc_idx2 = slc_idx_arr[region_int_idx]
                    #inds2 = self.decodeIndices(enc_idx2)
                    #print(region_typ_idx, (region_inds[0], region_int_idx), enc_idx2, enc_idx3)
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
        #print(self.getBoardPrintString(self.stateArray2Board(state_bm), self.box_shape))
        #print(opts_count_dict)
        self._simplifyState(state_bm, opts_count_dict, region_available_nums_bm, region_available_spaces_bm, enc_inds_changed)

        #print(self.getBoardPrintString(self.stateArray2Board(state_bm), self.box_shape))
        #print(opts_count_dict)
        #num_mx = self.board_side_length
        #n_small_sq = num_mx * num_mx

        def recur(
            state_bm: np.ndarray,
            opts_count_dict: SortedDict,
            region_available_nums_bm: np.ndarray,
            region_available_spaces_bm: np.ndarray,
        ) -> Generator[list[list[list[int]]], None, None]:
            #print(region_available_nums_bm)
            #print(region_available_spaces_bm)
            #print(self.getBoardPrintString(self.stateArray2Board(state_bm), self.box_shape))
            #print(state_bm)
            #print(opts_count_dict)
            if not opts_count_dict:
                #print("solution found")
                yield self.stateArray2Board(state_bm)
                #print(region_available_nums_bm)
                #print(region_available_spaces_bm)
                return
            
            dtype = state_bm.dtype.type
            if dtype == object: dtype = int
            #print(f"dtype = {dtype}")
            
            n_opts, enc_inds = opts_count_dict.peekitem(0)
            #print(opts_count_dict)
            enc_idx = next(iter(enc_inds))
            idx1, idx2 = self.decodeIndices(enc_idx)
            for j in self.bitmaskIndicesGenerator(state_bm[idx1, idx2]):
                #print(f"setting enc_idx {enc_idx} (({idx1}, {idx2})) to {j + 1}")
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
                #print(state_bm2)
                #print(opts_count_dict2)
                if self._simplifyState(state_bm2, opts_count_dict2, region_available_nums_bm2, region_available_spaces_bm2, {enc_idx}):
                    #print(self.getBoardPrintString(self.stateArray2Board(state_bm2), self.box_shape))
                    #print(state_bm)
                    #print(state_bm2)
                    #print(opts_count_dict2)
                    #mult_opts_cnt = 0
                    #for i1 in range(self.board_side_length):
                    #    for i2 in range(self.board_side_length):
                    #        n_opts3 = int(state_bm2[i1, i2]).bit_count()
                    #        if n_opts3 <= 1: continue
                    #        mult_opts_cnt += 1
                    #        enc_idx3 = self.encodeIndices(i1, i2)
                    #        if enc_idx3 not in opts_count_dict2.get(n_opts3, set()):
                    #            print(f"the number of options for position ({i1}, {i2}) (encoded {enc_idx3}) is inconsistent between the state array and the options count dictionary")
                    #            print(f"bitmask for element encoded index {enc_idx3} = {format(state_bm2[i1, i2], 'b')}, n_opts = {n_opts3}, set of encoded indices with 3 options = {opts_count_dict2.get(n_opts3, set())}")
                    #if mult_opts_cnt != sum(len(x) for x in opts_count_dict2.values()):
                    #    print(f"the number of elements with multiple options is inconsistent between the state array and the options count dictionary")
                    #print("calling recur()")
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
    #filename_in = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../sudoku_csv_files/three_by_two/easy1.csv")
    #filename_in = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../sudoku_csv_files/two_by_three/easy1.csv")
    filename_in = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../sudoku_csv_files/{filename}"))
    sudoku = Sudoku.loadSudokuFromCSV(filename_in)
    print(sudoku)
    """
    side_len = sudoku.board_side_length
    for i1 in range(side_len):
        for i2 in range(side_len):
            enc_idx = sudoku.encodeIndices(i1, i2)
            row_idx, col_idx, box_idx = sudoku.getRegionIndicesFromPosition(i1, i2) 
            print((i1, i2), enc_idx, sudoku.getBoxSlice(box_idx))
    """
    sol_cnt = 0
    since = time.time()
    for sol in sudoku.solutionsGenerator():
        sol_cnt += 1
        print(f"Solution {sol_cnt}")
        print(sudoku.getBoardPrintString(sol, sudoku.box_shape, initial_numbers_bold=True))
        print(f"solution is {'' if sudoku.checkSolutionValid(sol) else 'in'}valid")
        print(f"total time to find solution {sol_cnt} = {(time.time() - since):.4f} seconds")
    print(f"time to search for all possible solutions = {(time.time() - since):.4f} seconds")
    print(f"total number of solutions = {sol_cnt}")
    
    return

if __name__ == "__main__":
    main()