## Problem text

This problem was asked by Apple.

A Collatz sequence in mathematics can be defined as follows. Starting with any positive integer:

    if n is even, the next number in the sequence is n / 2
    if n is odd, the next number in the sequence is 3n + 1

It is conjectured that every such sequence eventually reaches the number 1. Test this conjecture.

Bonus: What input n <= 1000000 gives the longest sequence

## Solution

#### python/collatz.py, python/test_collatz.py

Wrote this mostly to make sure my Python env was working - I'm using uv for the first time - and to get the answer

#### python/async_collatz.py

The solution is easy, so I expanded by writing an answer to explore asyncio module.  I'm not sure I did it quite
right - I have to put in a sleep to get any worker other than the first to process any numbers.  But that could
just be because the computation is so fast, and I don't think asyncio helps much with compute bound (probably why
it's called _io_)

#### python/claude_flask.py, python/claude_asyncio.py -> python/claude_asyncio_w_worker_stats.py

To get some IO bounding, I decided to create an http server to do the computation.  I also decided to explore
Claude AI starting at this step.  Wow.  It created the flask app, and an asyncio version of collatz on the first
try.  I wanted to verify that multiple workers were running, so Claude added the worker stats.  I've used tqdm
before, but wouldn't have thought to use it here.  I added argparse section because I ran out of Claude prompts
for the day.

#### go/http.go

Also created by Claude.  And quite a bit faster than the flask app

