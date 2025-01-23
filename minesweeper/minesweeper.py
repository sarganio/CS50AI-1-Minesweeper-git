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


    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        # Keep track of cells known to be safe or mines
        self.safes = set()
        self.mines = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        raise self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safe

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -=1
        self.mines.add(cell)


    def reduce_sentences(self, other):
        if self.cells.issubset(other.cells):
                other.cells.difference_update(self.cells)
                other.count -=self.count
                return True

        if other.cells.issubset(self.cells):
            self.cells.difference_update(other.cells)
            self.count -= other.count
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
            
        # if all mine
        elif len(self.cells) == self.count:
            for cell in set(self.cells):
                self.mark_mine(cell)



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
        newKnoledge = Sentence(self.get_nearby_cells(cell), count)
        # mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for newCell in set(newKnoledge.cells):
            if newCell in self.safes:
                newKnoledge.mark_safe(newCell)
            if newCell in self.mines:
                newKnoledge.mark_mine(newCell)
        # add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        newKnoledge.mark_if_deterministic()
        for sentence in self.knowledge:
            newKnoledge.reduce_sentences(sentence)
            sentence.mark_if_deterministic()
    
        self.knowledge.append(newKnoledge)
        for safeCell in self.safes:
            for sentence in self.knowledge:
                if safeCell in sentence.cells:
                    sentence.mark_safe(safeCell)
        # iterate over all safe cells in all sentences and add them to base knoledge
        for sentence in self.knowledge:
            for cellToMark in sentence.safes:
                self.mark_safe(cellToMark)
            for cellToMark in set(sentence.mines):
                self.mark_mine(cellToMark)
        # remove exosted sentences
        for sentence in self.knowledge:
            if sentence.count == 0:
                self.knowledge.remove(sentence)
        # for debug:
        for sentence in self.knowledge:
            print(sentence) 
        print("safe moves to play:",list(self.safes.difference(self.moves_made)))
        print("known mines: ", self.mines)
        
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
                if (i,j) not in self.moves_made and (i,j) not in self.mines:
                    return (i,j)
    
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
                nearbyCells.add((i,j))
                
        return nearbyCells
