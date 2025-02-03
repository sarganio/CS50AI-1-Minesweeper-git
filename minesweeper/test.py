from minesweeper import MinesweeperAI, Sentence

def print_ai_status(move, nearby_count):
    print(f'\nAfter move:{move} with nearby_count:{nearby_count}')
    if ai.knowledge:
        print('Sentences in Knowledge Base:')
        for cnt, s in enumerate(ai.knowledge):
            #print(f'S#{cnt}: {s}')
            # create list from cell set with moves ordered by row/column
            s_as_l = sorted(list(s.cells), key=lambda t: (t[0], t[1]))
            print(f'S#{cnt}: {s_as_l} = {s.count}')
    else:
        print('NO Sentences in Knowledge Base.')       
    print(f'Safe Cells: {sorted(list(ai.safes))}')
    print(f'Mine Cells: {sorted(list(ai.mines))}')    
 # Create AI agent
HEIGHT, WIDTH, MINES = 8, 8, 8
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

s1 = Sentence({(0,0), (0,1), (1,0)}, 0)
print( s1.known_safes() ) # should return: {(0,0), (0,1), (1,0)}
print( s1.known_mines() ) # should return: set()

s2 = Sentence({(6,6), (6,7)}, 2)
print( s2.known_safes() ) # should return: set()
print( s2.known_mines() ) # should return: {(6,6), (6,7)}

s3 = Sentence({(3,3), (3,4), (3,5)}, 1)
print( s3.known_safes() ) # should return: set()
print( s3.known_mines() ) # should return: set()

# Test 1: Basic safe move detection
move, nearby_count = (1,2), 2
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

# Test 2: Adding a new sentence to knowledge base
move, nearby_count = (2,1), 0
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

# Test 3: Inferring a mine from existing knowledge
move, nearby_count = (0,4), 1
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

# Test 4: Inferring safe moves and mines after several updates
move, nearby_count = (0,3), 1
ai.add_knowledge(move, nearby_count)
ai.mark_mine((1,4))
print_ai_status(move, nearby_count)

# Test 5: Subset-based inference
move, nearby_count = (0,4), 0
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

# Test 6: Move near the edge of the board
move, nearby_count = (4,4), 1
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

# Test 7: Another safe move detection
move, nearby_count = (3,4), 0
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

move, nearby_count = (1,4), 1
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

move, nearby_count = (3,0), 2
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)

move, nearby_count = (3,3), 0
ai.add_knowledge(move, nearby_count)
print_ai_status(move, nearby_count)