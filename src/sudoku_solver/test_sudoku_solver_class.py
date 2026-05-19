from sudoku_solver_class import Sudoku
import pytest

def test_SudokuManualInitialization_valid() -> None:
    
    boards = []
    box_shapes = []

    boards.append([[1]])
    box_shapes.append((1, 1))

    boards.append([[0]])
    box_shapes.append((1, 1))

    boards.append(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    box_shapes.append((2, 2))

    boards.append(
        [
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    box_shapes.append((2, 2))

    boards.append(
        [
            [7,8,0,4,0,0,1,2,0],
            [6,0,0,0,7,5,0,0,9],
            [0,0,0,6,0,1,0,7,8],
            [0,0,7,0,4,0,2,6,0],
            [0,0,1,0,5,0,9,3,0],
            [9,0,4,0,6,0,0,0,5],
            [0,7,0,3,0,0,0,1,2],
            [1,2,0,0,0,7,4,0,0],
            [0,4,9,2,0,6,0,0,7],
        ]
    )
    box_shapes.append((3, 3))
    boards.append(
        [
            [1,2,0,4,0,5],
            [4,6,0,0,2,0],
            [0,0,0,6,4,1],
            [0,4,5,3,0,0],
            [6,0,4,1,0,2],
            [0,0,6,0,3,4],
        ]
    )
    box_shapes.append((3, 2))
    boards.append(
        [
            [1,4,0,0,6,0],
            [2,6,0,4,0,0],
            [0,0,0,5,4,6],
            [4,0,6,3,1,0],
            [0,2,4,0,0,3],
            [5,0,1,0,2,4],
        ]
    )
    box_shapes.append((2, 3))

    for board, box_shape in zip(boards, box_shapes):
        sudoku = Sudoku(board, box_shape)
        assert sudoku._box_shape == tuple(box_shape)
        assert sudoku._initial_board == tuple(tuple(x) for x in board)
    return


def test_SudokuManualInitialization_invalid() -> None:
    
    # Invalid box size format
    with pytest.raises(TypeError):
        Sudoku([], 5)
    with pytest.raises(ValueError):
        Sudoku([], ())
    with pytest.raises(ValueError):
        Sudoku([], (5,))
    with pytest.raises(ValueError):
        Sudoku([], (5, 5, 5))
    with pytest.raises(TypeError):
        Sudoku([], (None, 3))
    with pytest.raises(TypeError):
        Sudoku([], (3, None))
    with pytest.raises(TypeError):
        Sudoku([], ("cat", 3))
    with pytest.raises(TypeError):
        Sudoku([], (3, "cat"))
    with pytest.raises(ValueError):
        Sudoku([], (0, 3))
    with pytest.raises(ValueError):
        Sudoku([], (3, 0))
    with pytest.raises(ValueError):
        Sudoku([], (-1, 3))
    with pytest.raises(ValueError):
        Sudoku([], (3, -1))

    # Invalid board format
    with pytest.raises(TypeError):
        Sudoku(None, (3, 3))
    with pytest.raises(TypeError):
        Sudoku(5, (3, 3))
    with pytest.raises(ValueError):
        Sudoku([5], (3, 3))
    with pytest.raises(TypeError):
        Sudoku([1], (1, 1))
    with pytest.raises(TypeError):
        Sudoku([1, 1, 1, 1, 1, 1, 1, 1, 1], (3, 3))
    with pytest.raises(ValueError):
        Sudoku([[]], (1, 1))
    with pytest.raises(ValueError):
        Sudoku([[]], (1, 1))
    with pytest.raises(ValueError):
        Sudoku([[1], [0]], (1, 1))
    with pytest.raises(TypeError):
        Sudoku([["cat"]], (1, 1))
    with pytest.raises(TypeError):
        Sudoku([[1.1]], (1, 1))
    with pytest.raises(ValueError):
        Sudoku([[2]], (1, 1))
    with pytest.raises(ValueError):
        Sudoku([[-1]], (1, 1))
    with pytest.raises(ValueError):
        Sudoku([[1], []], (2, 1))
    with pytest.raises(ValueError):
        Sudoku([[1], [0, 0]], (2, 1))
    with pytest.raises(ValueError):
        Sudoku([[1], [3]], (2, 1))

    # Inconsistent board shape for given box shape
    boards = []
    box_shapes = []

    boards.append([[1]])
    box_shapes.append((1, 2))

    boards.append([[0]])
    box_shapes.append((2, 1))
    
    boards.append(
        [
            [7,8,0,4,0,0,1,2,0],
            [6,0,0,0,7,5,0,0,9],
            [0,0,0,6,0,1,0,7,8],
            [0,0,7,0,4,0,2,6,0],
            [0,0,1,0,5,0,9,3,0],
            [9,0,4,0,6,0,0,0,5],
            [0,7,0,3,0,0,0,1,2],
            [1,2,0,0,0,7,4,0,0],
            [0,4,9,2,0,6,0,0,7],
        ]
    )
    box_shapes.append((3, 2))
    boards.append(
        [
            [1,2,0,4,0,5],
            [4,6,0,0,2,0],
            [0,0,0,6,4,1],
            [0,4,5,3,0,0],
            [6,0,4,1,0,2],
            [0,0,6,0,3,4],
        ]
    )
    box_shapes.append((3, 3))
    boards.append(
        [
            [1,4,0,0,6,0],
            [2,6,0,4,0,0],
            [0,0,0,5,4,6],
            [4,0,6,3,1,0],
            [0,2,4,0,0,3],
            [5,0,1,0,2,4],
        ]
    )
    box_shapes.append((3, 2))
    for board, box_shape in zip(boards, box_shapes):

        with pytest.raises(ValueError):
            Sudoku(board, box_shape)
    
    # Immediate conflict
    boards = []
    box_shapes = []

    boards.append(
        [
            [1, 0, 0, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    box_shapes.append((2, 2))
    boards.append(
        [
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 0, 0, 0],
        ]
    )
    box_shapes.append((2, 2))
    boards.append(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    box_shapes.append((2, 2))
    return

def test_solutionGenerator() -> None:
    boards = []
    box_shapes = []
    sols = []

    boards.append([[1]])
    box_shapes.append((1, 1))
    sols.append(sorted([[[1]]]))

    boards.append([[0]])
    box_shapes.append((1, 1))
    sols.append(sorted([[[1]]]))
    
    boards.append(
        [
            [1, 2, 0, 0],
            [0, 0, 1, 2],
            [0, 1, 2, 0],
            [0, 0, 0, 1],
        ]
    )
    box_shapes.append((2, 2))
    sols.append(
        sorted(
            [
                [
                    [1, 2, 3, 4],
                    [3, 4, 1, 2],
                    [4, 1, 2, 3],
                    [2, 3, 4, 1],
                ],
                [
                    [1, 2, 4, 3],
                    [4, 3, 1, 2],
                    [3, 1, 2, 4],
                    [2, 4, 3, 1],
                ],
            ]
        )
    )

    boards.append(
        [
            [1, 2, 3, 4],
            [0, 0, 1, 2],
            [3, 1, 2, 0],
            [0, 0, 0, 1],
        ]
    )
    box_shapes.append((2, 2))
    sols.append([])

    
    boards.append(
        [
            [7,8,0,4,0,0,1,2,0],
            [6,0,0,0,7,5,0,0,9],
            [0,0,0,6,0,1,0,7,8],
            [0,0,7,0,4,0,2,6,0],
            [0,0,1,0,5,0,9,3,0],
            [9,0,4,0,6,0,0,0,5],
            [0,7,0,3,0,0,0,1,2],
            [1,2,0,0,0,7,4,0,0],
            [0,4,9,2,0,6,0,0,7],
        ]
    )
    box_shapes.append((3, 3))
    sols.append(
        [
            [
                [7, 8, 5, 4, 3, 9, 1, 2, 6],
                [6, 1, 2, 8, 7, 5, 3, 4, 9],
                [4, 9, 3, 6, 2, 1, 5, 7, 8],
                [8, 5, 7, 9, 4, 3, 2, 6, 1],
                [2, 6, 1, 7, 5, 8, 9, 3, 4],
                [9, 3, 4, 1, 6, 2, 7, 8, 5],
                [5, 7, 8, 3, 9, 4, 6, 1, 2],
                [1, 2, 6, 5, 8, 7, 4, 9, 3],
                [3, 4, 9, 2, 1, 6, 8, 5, 7],
            ]
        ]
    )

    boards.append(
        [
            [1,2,0,4,0,5],
            [4,6,0,0,2,0],
            [0,0,0,6,4,1],
            [0,4,5,3,0,0],
            [6,0,4,1,0,2],
            [0,0,6,0,3,4],
        ]
    )
    box_shapes.append((3, 2))
    sols.append(
        [
            [
                [1, 2, 3, 4, 6, 5],
                [4, 6, 1, 5, 2, 3],
                [3, 5, 2, 6, 4, 1],
                [2, 4, 5, 3, 1, 6],
                [6, 3, 4, 1, 5, 2],
                [5, 1, 6, 2, 3, 4],
            ],
        ]
    )
    
    boards.append(
        [
            [1, 4, 0, 0, 6, 0],
            [2, 6, 0, 4, 0, 0],
            [0, 0, 0, 5, 4, 6],
            [4, 0, 6, 3, 1, 0],
            [0, 2, 4, 0, 0, 3],
            [5, 0, 1, 0, 2, 4],
        ]
    )
    box_shapes.append((2, 3))
    sols.append(
        [
            [
                [1, 4, 3, 2, 6, 5],
                [2, 6, 5, 4, 3, 1],
                [3, 1, 2, 5, 4, 6],
                [4, 5, 6, 3, 1, 2],
                [6, 2, 4, 1, 5, 3],
                [5, 3, 1, 6, 2, 4]
            ],
        ]
    )

    for board, box_shape, sol in zip(boards, box_shapes, sols):
        sudoku = Sudoku(board, box_shape)
        assert sorted(list(sudoku.solutionsGenerator())) == sol
    return