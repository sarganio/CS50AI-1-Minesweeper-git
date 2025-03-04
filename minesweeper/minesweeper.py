import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    safes = set()
    mines = set()

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        # Keep track of cells known to be safe or mines

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        self.mark_if_deterministic()
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        self.mark_if_deterministic()
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        self.mines.add(cell)

    def reduce_sentence(self, other):
        if self.is_empty() or other.is_empty() == set() or self is other:
            return False  
               
        if self.cells.issubset(other.cells):
            # in order to change
            tempSen = Sentence(other.cells.difference(self.cells), other.count - self.count)
            other.cells = self.cells
            other.count = self.count
            self.cells = tempSen.cells
            self.count = tempSen.count
            self.mark_if_deterministic()
            return True

        if other.cells.issubset(self.cells):
            self.cells.difference_update(other.cells)
            self.count -= other.count
            self.mark_if_deterministic()
            return True
        
        largeSen = Sentence([], 0)
        smallSen = Sentence([], 0)
        if self.count > other.count:
            largeSen.cells = self.cells
            largeSen.count = self.count
            smallSen.cells = other.cells
            smallSen.count = other.count
        else:
            largeSen.cells = other.cells
            largeSen.count = other.count
            smallSen.cells = self.cells
            smallSen.count = self.count

        intersection = largeSen.cells.intersection(smallSen.cells)
        cellsInLargeNotInBoth = largeSen.cells.difference(intersection)

        if largeSen.count - len(cellsInLargeNotInBoth) == smallSen.count:
            for cell in smallSen.cells.difference(intersection):
                smallSen.mark_safe(cell)
            return True
         
        return False

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.safes.add(cell)
        if cell in self.cells:
            self.cells.remove(cell)
        
    def mark_if_deterministic(self):
        # if none are mines
        if self.count == 0:
            for cell in set(self.cells):
                self.mark_safe(cell)
            return True
            
        # if all mines
        elif len(self.cells) == self.count:
            for cell in set(self.cells):
                self.mark_mine(cell)
            return True
        return False
    
    def is_empty(self):
        return self.cells == set() and self.count == 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)       

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark the cell as a move that has been made
        self.moves_made.add(cell)
        # mark the cell as safe
        self.mark_safe(cell)
        # create a new sentence based on the value of `cell` and `count`
        newKnowledge = Sentence(self.get_nearby_cells(cell), count)
        # add exist knoledge about safe cells and mines in new sentence(for new condition update)
        self.update_marks_to(newKnowledge)
        # if the new statement added new information updates the AI mines and safes knowledge
        if newKnowledge.mark_if_deterministic():
            self.update_knowledge_marks_from(newKnowledge)
        # add the new sentence if not already exhausted its value
        if not newKnowledge.is_empty():
            self.knowledge.append(newKnowledge)
        self.conclude_new_information()

    def conclude_new_information(self):
        beforeSafes = set(self.safes)
        beforeMines = set(self.mines)
        for i in range(len(self.knowledge)):
            for j in range(i, len(self.knowledge)):
                self.update_knowledge_marks_from(self.knowledge[i])
                self.update_marks_to(self.knowledge[i])
                if i == j:
                    continue
                self.knowledge[i].reduce_sentence(self.knowledge[j])
                self.update_knowledge_marks_from(self.knowledge[i])      
        for sen in list(self.knowledge):
            if sen.is_empty():
                self.knowledge.remove(sen)
        if not (beforeSafes == self.safes and beforeMines == self.mines):
            self.conclude_new_information()

    def update_marks_to(self, newKnoledge):
        for safeCell in self.safes:
            newKnoledge.mark_safe(safeCell)
        for mineCell in self.mines:
            newKnoledge.mark_mine(mineCell)
    """         for newCell in set(newKnoledge.cells):
            if newCell in self.safes:
                newKnoledge.mark_safe(newCell)
            if newCell in self.mines:
                newKnoledge.mark_mine(newCell) """

    def update_knowledge_marks_from(self, sentence):
        for cellToMark in set(sentence.safes):
            self.mark_safe(cellToMark)
        for cellToMark in set(sentence.mines):
            self.mark_mine(cellToMark)
        for sen in self.knowledge:
            sen.mark_if_deterministic()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    return (i, j)
    
    def get_nearby_cells(self, cell):
        nearbyCells = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # skip cells outside board game
                if i == self.height or j == self.width or i < 0 or j < 0:
                    continue
                # add neighboring cell to nearby cell set
                nearbyCells.add((i, j))
                
        return nearbyCells