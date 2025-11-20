import sys
import time
import psutil

DELTA = 30
ALPHA = {
    ('A','A'):0, ('A','C'):110, ('A','G'):48,  ('A','T'):94,
    ('C','A'):110, ('C','C'):0, ('C','G'):118, ('C','T'):48,
    ('G','A'):48,  ('G','C'):118, ('G','G'):0, ('G','T'):110,
    ('T','A'):94,  ('T','C'):48,  ('T','G'):110, ('T','T'):0
}

class Node():

    def __init__(self, pre: object, penalty: int, seq1: str, seq2: str):
        self.seq1 = seq1
        self.seq2 = seq2
        self.penalty = penalty
        self.pre = pre

def generate_strings(path):
    try:
        with open(path) as f:
            lines = [ln.strip() for ln in f]
    except FileNotFoundError:
        print("Cannot open input file:", path)
        sys.exit(1)

    idx = 0
    s1 = lines[idx]; idx += 1
    cur = s1
    while idx < len(lines) and lines[idx].isdigit():
        k = int(lines[idx])
        cur = cur[:k+1] + cur + cur[k+1:]
        idx += 1
    s1 = cur

    s2 = lines[idx]; idx += 1
    cur = s2
    while idx < len(lines) and lines[idx].isdigit():
        k = int(lines[idx])
        cur = cur[:k+1] + cur + cur[k+1:]
        idx += 1
    s2 = cur

    return s1, s2

def get_align_penalty(seq1: str, seq2: str):
    gap = DELTA
    alpha = ALPHA.get
    length = len(seq1) + 1
    width = len(seq2) + 1
    board = [[0] * width for _ in range(2)]
    board[0][0] = 0
    board[1][0] = gap

    for j in range(1, width):
        board[0][j] = board[0][j - 1] + gap

    for i in range(1, length):
        board[1][0] = board[0][0] + gap  # vertical move at first column
        for j in range(1, width):
            diag = board[0][j - 1] + (0 if seq1[i - 1] == seq2[j - 1] else alpha((seq1[i - 1], seq2[j - 1])))
            left = board[1][j - 1] + gap  # horizontal move
            up   = board[0][j] + gap      # vertical move
            board[1][j] = min(diag, left, up)
        board[0][:] = board[1][:]
        board[1][0] = board[0][0] + gap

    return board[1]

def hirschberg(seq1: str, seq2: str, align1: list, align2: list):
    if len(seq1) <= 2 or len(seq2) <= 2:
        board = create_board(seq1, seq2)
        align_seq = create_align_seq(board)
        align1[0] += align_seq[0]  
        align2[0] += align_seq[1]
        return board[-1][-1].penalty
    
    else:
        mid1 = len(seq1) // 2
        left1 = seq1[:mid1]
        right1 = seq1[mid1:]
        penalty1 = get_align_penalty(left1, seq2)
        penalty2 = get_align_penalty(right1[::-1], seq2[::-1])
        sum_pen = [0] * len(penalty1)
        
        l, r = 0, len(sum_pen) - 1
        min_pen = float('inf')
        idx = -1

        for i in range(len(sum_pen)):
            sum_pen[i] = penalty1[l] + penalty2[r]
            if sum_pen[i] < min_pen:
                min_pen = sum_pen[i]
                idx = i
            l += 1
            r -= 1
        left2 = seq2[:idx]
        right2 = seq2[idx:]
        return hirschberg(left1, left2, align1, align2) + hirschberg(right1, right2, align1, align2)
    
def create_board(seq1: str,  seq2: str):
    alpha = ALPHA.get
    gap = DELTA
    length = len(seq1) + 1
    width = len(seq2) + 1
    board = [[None for _ in range(width)] for _ in range(length)]
    board[0][0] = Node(pre=None, penalty=0, seq1='#', seq2='#')

    for j in range(1, width):
        board[0][j] = Node(board[0][j - 1], board[0][j - 1].penalty + gap, '_', seq2[j - 1])
    for i in range(1, length):
        board[i][0] = Node(board[i - 1][0], board[i - 1][0].penalty + gap, seq1[i - 1], '_')
    
    for i in range(1, length):
        for j in range(1, width):
            if seq1[i - 1] == seq2[j - 1]:
                board[i][j] = Node(board[i - 1][j - 1], board[i - 1][j - 1].penalty, seq1[i - 1], seq2[j - 1])
            else:
                min_pen = float('inf')
                if board[i - 1][j - 1].penalty + alpha((seq1[i - 1], seq2[j - 1])) < min_pen:
                    min_pen = board[i - 1][j - 1].penalty + alpha((seq1[i - 1], seq2[j - 1]))
                    board[i][j] = Node(board[i - 1][j - 1], min_pen, seq1[i - 1], seq2[j - 1])
                if board[i][j - 1].penalty + gap < min_pen:
                    min_pen = board[i][j - 1].penalty + gap
                    board[i][j] = Node(board[i][j - 1], min_pen, '_', seq2[j - 1])
                if board[i - 1][j].penalty + gap < min_pen:
                    min_pen = board[i - 1][j].penalty + gap
                    board[i][j] = Node(board[i - 1][j], min_pen, seq1[i - 1], seq2[j - 1])
    
    return board

def create_align_seq(board: list[list[Node]]):
    length = len(board)
    width = len(board[length - 1])
    str1 = ''
    str2 = ''
    temp = board[length - 1][width - 1] 
    while temp.seq1 != '#' and temp.seq2 != '#':
        str1 += temp.seq1
        str2 += temp.seq2
        temp = temp.pre
    return [str1[::-1], str2[::-1]]

def memory_kb():
    p = psutil.Process()
    return int(p.memory_info().rss / 1024)

def get_time_in_milliseconds():
    return time.time() * 1000

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 basic.py <input_file> <output_file>")
        sys.exit(1)

    inp, outp = sys.argv[1], sys.argv[2]
    s1, s2 = generate_strings(inp)

    start = time.time()
    align1 = ['']
    align2 = ['']
    penalty = hirschberg(s1, s2, align1, align2)
    end = time.time()

    elapsed_ms = (end - start) * 1000
    mem_used = memory_kb()

    with open(outp, "w") as f:
        f.write(f"{penalty}\n")
        f.write(align1[0] + "\n")
        f.write(align2[0] + "\n")
        f.write(f"{elapsed_ms}\n")
        f.write(f"{mem_used}\n")

if __name__ == "__main__":
    main()