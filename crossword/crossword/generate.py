import sys

from crossword import *
import random


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.crossword.variables:
            for word in self.domains[v].copy():
                Length = v.length
                if len(word) != Length:
                    self.domains[v].remove(word)
            #print (self.domains[v])
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
    
        (i,j) = self.crossword.overlaps[x,y]
        for word in self.domains[x].copy():
            boolean = False
            for w in self.domains[y]:
                if word[i] == w[j]:
                    boolean = True
                    revised = True
            if boolean == False:
                self.domains[x].remove(word)
        #print(self.domains[x])
        return revised
        #raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        if arcs == None:
            arcs = []
            variableSet = self.crossword.variables.copy()
            while len(variableSet)>0:
                variable1 = random.choice(list(variableSet))
                variableSet.remove(variable1)
                for variable2 in variableSet:
                    if self.crossword.overlaps[variable1, variable2] != None:
                        arcs.append((variable1, variable2))
        #print (arcs)

        while len(arcs)>0:
            (v1, v2) = arcs[0]
            revised = self.revise(v1, v2)
            arcs.pop(0)
            if revised == True:
                if len(self.domains[v1]) == 0:
                    return False
                for variable2 in self.crossword.neighbors(v1):
                    if variable2 != v2 and ((v1, variable2) not in arcs) :
                        arcs.append((variable2, v1))
            #print (arcs)
            
    
        return True

       # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for v in self.crossword.variables:
            if v not in assignment.keys():
                return False
        return True
        #raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(set(assignment.values())) != len(assignment.values()):
            return False
        for v in assignment.keys():
            if len(assignment[v]) != v.length:
                return False
            for neighbour in self.crossword.neighbors(v):
                if neighbour in assignment:
                    (i, j) = self.crossword.overlaps[neighbour, v]
                    if assignment[neighbour][i] != assignment[v][j]:
                        return False
        return True

        #raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        def key(x):
            count = 0
            for neighbour in self.crossword.neighbors(var):
                (i, j) = self.crossword.overlaps[neighbour, var]
                for q in self.domains[neighbour]:
                    if q[i] != x[j]:
                        count += 1
            return count

        return sorted(list(self.domains[var]), key=key)                                        

        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_v = None
        for v in self.crossword.variables:
            if v not in assignment.keys():
                if min_v is None:
                    min_v = v
                elif len(self.domains[v]) < len (self.domains[min_v]):
                    min_v = v
                elif len(self.domains[v]) == len (self.domains[min_v]):
                    if len(self.crossword.neighbors(v)) >= len(self.crossword.neighbors(min_v)):
                        min_v = v
        return min_v
        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #print (assignment)
        if self.assignment_complete(assignment) :
            return assignment
        variable1 = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(variable1, assignment):
            assignment[variable1] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result !=None:
                    return result
            assignment.pop(variable1)
        return None
        #raise NotImplementedError


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    #structure = "C:/Users/bhavn/Documents/Harward CS50 AI/projects/crossword/crossword/data/structure2.txt"
    #words = "C:/Users/bhavn/Documents/Harward CS50 AI/projects/crossword/crossword/data/words2.txt"
    #output = None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
