import unittest
import minesweeper
from unittest.mock import patch

class TestMinesweeper(unittest.TestCase):

    def setUp(self):
        """Set up a Minesweeper instance for testing."""
        self.minesweeper = minesweeper.Minesweeper(height=4, width=4, mines=3)

    def test_is_mine(self):
        """Test if is_mine correctly identifies a mine."""
        for mine in self.minesweeper.mines:
            self.assertTrue(self.minesweeper.is_mine(mine))

        non_mines = [(i, j) for i in range(self.minesweeper.height) for j in range(self.minesweeper.width) if (i, j) not in self.minesweeper.mines]
        for cell in non_mines:
            self.assertFalse(self.minesweeper.is_mine(cell))

    def test_nearby_mines(self):
        """Test the nearby_mines method for correctness."""
        # Manually place mines for predictable testing
        self.minesweeper.board = [[False] * 4 for _ in range(4)]
        self.minesweeper.board[1][1] = True  # Mine at (1, 1)
        self.minesweeper.board[2][2] = True  # Mine at (2, 2)
        self.minesweeper.board[3][3] = True  # Mine at (3, 3)

        self.assertEqual(self.minesweeper.nearby_mines((0, 0)), 1)
        self.assertEqual(self.minesweeper.nearby_mines((1, 0)), 1)
        self.assertEqual(self.minesweeper.nearby_mines((1, 1)), 1)
        self.assertEqual(self.minesweeper.nearby_mines((2, 2)), 2)
        self.assertEqual(self.minesweeper.nearby_mines((3, 2)), 2)

    def test_won(self):
        """Test the won method to verify victory conditions."""
        self.minesweeper.mines_found = self.minesweeper.mines.copy()
        self.assertTrue(self.minesweeper.won())

        self.minesweeper.mines_found = set()
        self.assertFalse(self.minesweeper.won())

class TestSentence(unittest.TestCase):

    def setUp(self):
        """Set up a Sentence instance for testing."""
        self.sentence = minesweeper.Sentence(cells={(1, 1), (2, 2)}, count=1)

    def test_known_mines(self):
        """Test if known_mines correctly identifies all mines."""
        self.sentence.mark_mine((1, 1))
        self.assertEqual(self.sentence.known_mines(), {(1, 1)})

    def test_known_safes(self):
        """Test if known_safes correctly identifies all safe cells."""
        self.sentence.mark_safe((2, 2))
        self.assertEqual(self.sentence.known_safes(), { (2, 2)})

    def test_mark_safe(self):
        """Test the mark_safe method."""
        self.sentence.mark_safe((2, 2))
        self.assertNotIn((2, 2), self.sentence.cells)
        self.assertIn((2, 2), self.sentence.safes)

    def test_mark_mine(self):
        """Test the mark_mine method."""
        self.sentence.mark_mine((1, 1))
        self.assertNotIn((1, 1), self.sentence.cells)
        self.assertIn((1, 1), self.sentence.mines)

class TestMinesweeperAI(unittest.TestCase):

    def setUp(self):
        """Set up a MinesweeperAI instance for testing."""
        self.ai = minesweeper.MinesweeperAI(height=4, width=4)

    def test_mark_mine(self):
        """Test the AI's ability to mark a mine."""
        self.ai.mark_mine((1, 1))
        self.assertIn((1, 1), self.ai.mines)
        for sentence in self.ai.knowledge:
            self.assertIn((1, 1), sentence.known_mines())

    def test_mark_safe(self):
        """Test the AI's ability to mark a safe cell."""
        self.ai.mark_safe((2, 2))
        self.assertIn((2, 2), self.ai.safes)
        for sentence in self.ai.knowledge:
            self.assertIn((2, 2), sentence.known_safes())

    def test_make_safe_move(self):
        """Test the AI's ability to make a safe move."""
        self.ai.safes.add((0, 0))
        self.ai.moves_made.add((1, 1))
        self.assertEqual(self.ai.make_safe_move(), (0, 0))

if __name__ == "__main__":
    unittest.main()
