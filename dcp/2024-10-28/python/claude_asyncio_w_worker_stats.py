import argparse
import asyncio
import aiohttp
from typing import Tuple, List, Dict
import time
from tqdm import tqdm
from dataclasses import dataclass
from collections import Counter


@dataclass
class CollatzResult:
    number: int
    sequence: List[int]
    sequence_length: int
    worker_id: int


class WorkerStats:
    def __init__(self):
        self.numbers_processed = 0
        self.total_sequence_length = 0
        self.longest_sequence = 0
        self.number_with_longest = 0
        self.processing_time = 0.0

    @property
    def avg_sequence_length(self):
        return (
            self.total_sequence_length / self.numbers_processed
            if self.numbers_processed > 0
            else 0
        )


async def get_collatz_sequence(
    number: int, session: aiohttp.ClientSession, base_url: str = "http://localhost:9090"
) -> List[int]:
    """
    Get Collatz sequence for a number by calling the Flask API asynchronously.
    """
    async with session.get(
        f"{base_url}/collatz", params={"number": number}
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return data["sequence"]


async def worker(
    name: int,
    base_url: str,
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    progress: tqdm,
    results: List[CollatzResult],
    stats: Dict[int, WorkerStats],
):
    """Worker to process numbers from the queue."""
    worker_stat = WorkerStats()
    stats[name] = worker_stat

    while True:
        try:
            number = await queue.get()
            if number is None:  # Poison pill
                queue.task_done()
                break

            start_time = time.time()
            sequence = await get_collatz_sequence(number, session, base_url)
            worker_stat.processing_time += time.time() - start_time

            # Update worker statistics
            worker_stat.numbers_processed += 1
            worker_stat.total_sequence_length += len(sequence)
            if len(sequence) > worker_stat.longest_sequence:
                worker_stat.longest_sequence = len(sequence)
                worker_stat.number_with_longest = number

            results.append(
                CollatzResult(
                    number=number,
                    sequence=sequence,
                    sequence_length=len(sequence),
                    worker_id=name,
                )
            )
            progress.update(1)
            queue.task_done()

        except Exception as e:
            print(f"\nWorker {name} error processing number {number}: {e}")
            queue.task_done()


async def process_numbers(
    max_number: int, num_workers: int = 5, base_url: str = "http://localhost:8080"
) -> Tuple[int, List[int], Dict[int, WorkerStats]]:
    """Process numbers up to max_number using multiple workers."""
    queue = asyncio.Queue()
    results: List[CollatzResult] = []
    worker_stats: Dict[int, WorkerStats] = {}

    # Fill the queue with numbers to process
    for num in range(1, max_number + 1):
        await queue.put(num)

    # Add poison pills for workers
    for _ in range(num_workers):
        await queue.put(None)

    progress = tqdm(total=max_number, desc="Processing numbers")

    async with aiohttp.ClientSession() as session:
        workers = [
            asyncio.create_task(
                worker(i, base_url, queue, session, progress, results, worker_stats)
            )
            for i in range(num_workers)
        ]

        await queue.join()
        await asyncio.gather(*workers)

    progress.close()

    longest_result = max(results, key=lambda x: x.sequence_length)
    return longest_result.number, longest_result.sequence, worker_stats


def print_worker_stats(stats: Dict[int, WorkerStats]):
    """Print detailed statistics for each worker."""
    print("\nWorker Statistics:")
    print("-" * 80)
    print(
        f"{'Worker ID':^10} | {'Numbers':^10} | {'Avg Length':^12} | {'Longest':^10} | {'Time (s)':^10}"
    )
    print("-" * 80)

    total_numbers = 0
    total_time = 0.0

    for worker_id, stat in sorted(stats.items()):
        print(
            f"{worker_id:^10} | {stat.numbers_processed:^10} | {stat.avg_sequence_length:^12.2f} | "
            f"{stat.longest_sequence:^10} | {stat.processing_time:^10.2f}"
        )
        total_numbers += stat.numbers_processed
        total_time += stat.processing_time

    print("-" * 80)
    print(f"Total numbers processed: {total_numbers}")
    print(f"Total processing time: {total_time:.2f} seconds")
    print(
        f"Average processing time per number: {(total_time/total_numbers)*1000:.2f} ms"
    )


async def main(max_number=10_000, num_workers=5, base_url="http://localhost:8080"):
    print(f"Finding the number with the longest Collatz sequence up to {max_number}")
    print(f"Using {num_workers} concurrent workers")

    try:
        start_time = time.time()
        number, sequence, worker_stats = await process_numbers(
            max_number, num_workers, base_url
        )
        end_time = time.time()

        print("\nResults:")
        print(f"Number with longest sequence: {number}")
        print(f"Sequence length: {len(sequence)}")
        print(f"Sequence: {sequence}")
        print(f"\nTotal time taken: {end_time - start_time:.2f} seconds")

        print_worker_stats(worker_stats)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Collatz Sequence")
    parser.add_argument("-w", "--num-workers", type=int, default=5, dest="num_workers")
    parser.add_argument(
        "-n", "--max-number", type=int, default=10_000, dest="max_number"
    )
    parser.add_argument(
        "-u", "--base-url", default="http://localhost:8080", dest="base_url"
    )

    args = parser.parse_args()
    print(args)
    asyncio.run(main(**vars(args)))
