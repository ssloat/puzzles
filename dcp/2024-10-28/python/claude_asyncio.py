import asyncio
import aiohttp
from typing import Tuple, List
import time
from tqdm import tqdm
from dataclasses import dataclass
from collections import deque


@dataclass
class CollatzResult:
    number: int
    sequence: List[int]
    sequence_length: int


async def get_collatz_sequence(
    number: int, session: aiohttp.ClientSession, base_url: str = "http://localhost:8080"
) -> CollatzResult:
    """
    Get Collatz sequence for a number by calling the Flask API asynchronously.

    Args:
        number: The number to calculate sequence for
        session: aiohttp client session
        base_url: The base URL of the Flask API

    Returns:
        CollatzResult containing the number and its sequence
    """
    async with session.get(
        f"{base_url}/collatz", params={"number": number}
    ) as response:
        response.raise_for_status()
        data = await response.json()
        sequence = data["sequence"]
        return CollatzResult(
            number=number, sequence=sequence, sequence_length=len(sequence)
        )


async def worker(
    name: int,
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    progress: tqdm,
    results: List[CollatzResult],
):
    """Worker to process numbers from the queue."""
    while True:
        try:
            number = await queue.get()
            if number is None:  # Poison pill
                queue.task_done()
                break

            result = await get_collatz_sequence(number, session)
            results.append(result)
            progress.update(1)
            queue.task_done()

        except Exception as e:
            print(f"\nWorker {name} error processing number {number}: {e}")
            queue.task_done()


async def process_numbers(
    max_number: int, num_workers: int = 5
) -> Tuple[int, List[int]]:
    """
    Process numbers up to max_number using multiple workers.

    Args:
        max_number: The maximum number to check
        num_workers: Number of concurrent workers

    Returns:
        Tuple of (number with longest sequence, the sequence itself)
    """
    queue = asyncio.Queue()
    results: List[CollatzResult] = []

    # Fill the queue with numbers to process
    for num in range(1, max_number + 1):
        await queue.put(num)

    # Add poison pills for workers
    for _ in range(num_workers):
        await queue.put(None)

    # Setup progress bar
    progress = tqdm(total=max_number, desc="Processing numbers")

    # Create client session for all workers to share
    async with aiohttp.ClientSession() as session:
        # Create workers
        workers = [
            asyncio.create_task(worker(i, queue, session, progress, results))
            for i in range(num_workers)
        ]

        # Wait for all workers to complete
        await queue.join()
        await asyncio.gather(*workers)

    progress.close()

    # Find the longest sequence
    longest_result = max(results, key=lambda x: x.sequence_length)
    return longest_result.number, longest_result.sequence


async def main():
    MAX_NUMBER = 100000
    NUM_WORKERS = 5

    print(f"Finding the number with the longest Collatz sequence up to {MAX_NUMBER}")
    print(f"Using {NUM_WORKERS} concurrent workers")

    try:
        start_time = time.time()
        number, sequence = await process_numbers(MAX_NUMBER, NUM_WORKERS)
        end_time = time.time()

        print("\nResults:")
        print(f"Number with longest sequence: {number}")
        print(f"Sequence length: {len(sequence)}")
        print(f"Sequence: {sequence}")
        print(f"\nTime taken: {end_time - start_time:.2f} seconds")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    # Install required packages:
    # pip install aiohttp tqdm
    asyncio.run(main())
