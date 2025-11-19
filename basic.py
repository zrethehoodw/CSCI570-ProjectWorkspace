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

def align_basic(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]

    for i in range(1, m+1):
        dp[i][0] = i * DELTA
    for j in range(1, n+1):
        dp[0][j] = j * DELTA

    alpha = ALPHA.get

    for i in range(1, m+1):
        for j in range(1, n+1):
            c_match = dp[i-1][j-1] + alpha((a[i-1], b[j-1]), 999999)
            c_gap_a = dp[i-1][j] + DELTA
            c_gap_b = dp[i][j-1] + DELTA
            dp[i][j] = min(c_match, c_gap_a, c_gap_b)

    aligned_a = []
    aligned_b = []
    i, j = m, n
    while i > 0 or j > 0:
        cost = dp[i][j]
        if i > 0 and j > 0 and cost == dp[i-1][j-1] + ALPHA[(a[i-1], b[j-1])]:
            aligned_a.append(a[i-1])
            aligned_b.append(b[j-1])
            i -= 1; j -= 1
        elif i > 0 and cost == dp[i-1][j] + DELTA:
            aligned_a.append(a[i-1])
            aligned_b.append('_')
            i -= 1
        else:
            aligned_a.append('_')
            aligned_b.append(b[j-1])
            j -= 1

    aligned_a.reverse()
    aligned_b.reverse()

    return dp[m][n], ''.join(aligned_a), ''.join(aligned_b)

def memory_kb():
    p = psutil.Process()
    return int(p.memory_info().rss / 1024)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 basic.py <input_file> <output_file>")
        sys.exit(1)

    inp, outp = sys.argv[1], sys.argv[2]
    s1, s2 = generate_strings(inp)

    start = time.time()
    cost, a1, a2 = align_basic(s1, s2)
    end = time.time()

    elapsed_ms = (end - start) * 1000
    mem_used = memory_kb()

    with open(outp, "w") as f:
        f.write(f"{cost}\n")
        f.write(a1 + "\n")
        f.write(a2 + "\n")
        f.write(f"{elapsed_ms}\n")
        f.write(f"{mem_used}\n")

if __name__ == "__main__":
    main()