import itertools
import random
import copy


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

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells)==self.count:
            return self.cells
        return set()
        #raise NotImplementedError
    
    def getcells(self):
        return self.cells

    def getcount(self):
        return self.count

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells
        return set()
        #raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count=self.count-1

       # raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        #raise NotImplementedError


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
        self.moves_made.add(cell)
        self.mark_safe(cell)
        cells=set()
        #print("yo")
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if  i>=0 and j>=0 and i<self.height and j<self.width:
                    if (i,j)==cell:
                        continue
                    if (i,j) in self.mines:
                        count=count-1

                    elif (i,j) not in self.safes and (i,j) not in self.moves_made:
                        cells.add((i,j))

        a=Sentence(cells, count)
        r=len(self.knowledge)
        #print("go")
        '''Ignore this code
        while i<r:
            if self.knowledge[i].getcells().issubset(a.cells):
                #self.knowledge.append(Sentence(cells-self.knowledge[i].getcells(), count-self.knowledge[i].getcount()))
                a=Sentence(cells-self.knowledge[i].getcells(), count-self.knowledge[i].getcount())
            if cells.issubset(self.knowledge[i].getcells()):
                self.knowledge[i]=Sentence(self.knowledge[i].getcells()-cells, self.knowledge[i].getcount()-count)
            i+=1
        '''
        self.knowledge.append(a)
        #print("no")
        r=range(len(self.knowledge))
        i=0
        while i<len(self.knowledge):
            if (self.knowledge[i].known_safes()!=set()):
                for cell in copy.deepcopy(self.knowledge[i].known_safes()):
                    self.mark_safe(cell)
                self.knowledge.pop(i)
            elif (self.knowledge[i].known_safes()!=set()):
                for cell in copy.deepcopy(self.knowledge[i].known_mines()):
                    self.mark_mine(cell)
                self.knowledge.pop(i)
            else: 
                i=i+1

        r=range(len(self.knowledge))

        for i in r:
            for j in range(i+1, len(self.knowledge)):
                if self.knowledge[i].getcells().issubset(self.knowledge[j].getcells()):
                #self.knowledge.append(Sentence(cells-self.knowledge[i].getcells(), count-self.knowledge[i].getcount()))
                    self.knowledge[j]=Sentence(self.knowledge[j].getcells()-self.knowledge[i].getcells(), self.knowledge[j].getcount()-self.knowledge[i].getcount())
                elif self.knowledge[j].getcells().issubset(self.knowledge[i].getcells()):
                    self.knowledge[i]=Sentence(self.knowledge[i].getcells()-self.knowledge[j].getcells(), self.knowledge[i].getcount()-self.knowledge[j].getcount())

        i=0
        while i<len(self.knowledge):
            if (self.knowledge[i].known_safes()!=set()):
                for cell in copy.deepcopy(self.knowledge[i].known_safes()):
                    self.mark_safe(cell)
                self.knowledge.pop(i)
            elif (self.knowledge[i].known_mines()!=set()):
                for cell in copy.deepcopy(self.knowledge[i].known_mines()):
                    self.mark_mine(cell)
                self.knowledge.pop(i)
            else: 
                i=i+1

        #print("mines",len(self.mines))
                       
        #raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i in self.safes:
            if i not in self.moves_made:
                return i
        #raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        s=set()
        for i in range(self.height):
            for j in range(self.width):
                s.add((i,j))

        s=s-self.mines-self.moves_made
        if s==set(): return None
        return random.choice(list(s))
        #raise NotImplementedError

'''Ignore this code
m = Minesweeper()
print(m)
ai=MinesweeperAI()
print("qwe")
move=ai.make_random_move()
print(move,"bhav")
ai.add_knowledge(move, m.nearby_mines(move))
print("Marok")
print(move)
for i in ai.knowledge:
    print(i.cells, i.count)
'''