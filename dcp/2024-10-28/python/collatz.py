from collections import namedtuple

Result = namedtuple('Result', 'num seq')

def seq(n: int) -> int:
    results = [n]
    while results[-1] != 1:
        if results[-1] % 2 == 0:
            results.append( int(results[-1] / 2) )
        else:
            results.append( 3*results[-1] + 1 )

    return results

# 837_799
def longest_collatz(size: int = 1_000_000) -> Result:
    result = Result(0, [])
    for n in range(1, size+1):
        s = seq(n)
        if len(s) > len(result.seq):
            result = Result(n, s)

    return result



def main():
    print("Hello world")
    print(collatz(5))

    result = longest_collatz()
    print(result.num, result.seq)


if __name__ == '__main__':
    main()

