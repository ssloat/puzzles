import asyncio
from typing import List
from dataclasses import dataclass

@dataclass
class Result:
    num: int
    seq: List[int]

async def worker(name, queue):
    while True:
        numbers = await queue.get()
        for n in numbers:
            s = await seq(n)
        #await asyncio.sleep(0.1)
        queue.task_done()

 #       if not name.endswith('-0'):
 #           print(f"{name} calculated {n}: {s}")

async def seq(n: int) -> List[int]:
    results = [n]
    while results[-1] != 1:
        if results[-1] % 2 == 0:
            results.append( int(results[-1] / 2) )
        else:
            results.append( 3*results[-1] + 1 )

    return results

async def main():
    step = 1_000
    queue = asyncio.Queue()
    numbers = list(range(1, 1_000_001))
    while numbers:
        queue.put_nowait(numbers[:step])
        numbers = numbers[step:]

#    for n in range(1, 1_000_001):
#        queue.put_nowait(n)

    tasks = []
    for n in range(3):
        task = asyncio.create_task(worker(f"worker-{n}", queue))
        tasks.append(task)

    await queue.join()
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    asyncio.run(main())


