# Profiling a python script

## tldr (AKA executive summary)

- use `cProfile` to see the total time, average time and # of calls
- use `pycallgraph` for visualization
- After all, the tools just give you insight. you still need to clean your own shit
	by reading your source code.

## Long story

Let's use the _famous_ Fibonacci numbers. If you are interested in the history
and applications of Fibonacci numbers, I suggest you to visit the [wikipedia
page](https://en.wikipedia.org/wiki/Fibonacci_number). The Fibonacci number is
defined as:

```
F(n) = F(n-1) + F(n-2)
```

with seed values (or base cases):

```
F(0) = 0, F(1) = 1
```

Please note that sometimes `F(1)` and `F(2)` is chosen as the seed values
instead. But `F(0)` and `F(1)` is used here because this makes programming
somewhat easier. 

Suppose you are asked to write a program `main.py` to compute the first 1000
Fibonacci numbers. The file looks like this:

```
def fibonacci(n):
	'''Return the n-th Fibonacci number.'''
	pass


for i in xrange(1000):
    print 'F({}) = {}'.format(i, fibonacci(i))
```

## First implementation

Let's start with using the definition to implement the `fibonacci()`. 

```
def fibonacci(n):
  if n == 0:
    return 0

  if n == 1:
    return 1

  return fibonacci(n-1) + fibonacci(n-2)
```

It is recursion implementation. And let's try this out with `python main.py`.
The program should run smoothly and print out the Fibonacci number blazingly
fast *UNTIL* `F(30)` depending your machine spec and states... It starts to
take one second to get `F(31)` and then a few seconds for `F(32)`. The time
needed just keeps increasing. It will take maybe years to compute `F(100)` let
alone `F(1000)`... I kill the program with `ctrl+c` before analyzing what's
worng in my program.

In this case, we can easily tell that the program is very slow. As a
programmer, just telling me the program is slow is not so helpful. What I
really need are:

1. Why the program is slow
2. How slow it is
3. A way to compare the speed of two programs given that they are performing
the same task

Let's address the first issue "Why the program is slow".

One way to do that is to "use the source, Luke". 

![Use the source, luke](http://www.bezdelnique.ru/wp-content/uploads/2009/08/use_source_luke.png)

The more "professional" way to say this is [Static program
analysis](https://en.wikipedia.org/wiki/Static_program_analysis). *Static
program analysis* is used not only for performance improvement but also
locating potentially vulnerable code by both black hats and white hats. We all
read code before. Let's try the "dynamic program analysis" which is "run the
program and see what will happen".

## Dynamic program analysis

We need to measure how slow our program is. The "easiest" way to time a program
is to use the `time` command. But it only tell us the total time the program
executes. It does not tell us anything about the internal of the program. This
time we need a *profiler* to time our program.

In general, a typical profiler (language independent) tells:

- how many times a function is called
- how much memory usage

Some profilers check for race condition, code coverage, network usage and so
on...

A profiler can help you to fix some of the *time limit exceed error* and *out
of memory error*. Python comes with a
[profiler](https://docs.python.org/2/library/profile.html). To use it, you can
import it in your python script or run it from the command line.

### Profiling the first implementation

To facilitate the profiling and testing, the `main.py` need to be updated. The
updated `main.py` is appended.

Let's find the 30-th Fibonacci number and see how bad our program is. (30
is where the program starts to become "slow".)

```
S=30 N=30 python -m cProfile -s time main.py
```

The output (truncated):

```
         2693037 function calls (501 primitive calls) in 0.836 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
2692537/1    0.828    0.000    0.828    0.828 main.py:6(fibonacci_v1)
        1    0.004    0.004    0.007    0.007 __init__.py:24(<module>)
        1    0.001    0.001    0.002    0.002 collections.py:11(<module>)
        1    0.001    0.001    0.836    0.836 main.py:3(<module>)
        1    0.001    0.001    0.001    0.001 heapq.py:31(<module>)
        1    0.000    0.000    0.001    0.001 threading.py:1(<module>)
        2    0.000    0.000    0.000    0.000 sre_parse.py:395(_parse)
```

The first column `ncalls` is number of call to the function. The function is
showed in the last column. `tottime` is the total time spent on this function.
Other columns are not that important at this moment. Sometimes there are two
numbers in the `ncalls` column. Quote from the doc.

> When there are two numbers in the first column (for example 3/1), it means
> that the function recursed. The second value is the number of primitive calls
> and the former is the total number of calls. Note that when the function does
> not recurse, these two values are the same, and only the single figure is
> printed.

So we have way too many calls to the function `fibonacci_v1()`.  Each time a
function is called in your program, some memory is used to store the current
state such the the value of the local variables of the program before going to
the function.  After executing the function, the program restores its previous
state.  It takes time and memory space to save/load the states. (This process
uses `stack`. `stack frame`, `call stack`, `stack trace` and `stack overflow`
are related.)  This function-call overhead _stacks_ up.  But I am not asking
you to write everything in one big function.  It might be executed fast but it
trades code readability and maintainability.  But this is the topic for another
day.  In our simple Fibonacci number example, memory might not be an issue. But
in GAE, the memory is limited to 128MB. It would be a big problem if your
program used too much memory.

There is another way to get some insights about the program. We can generate a
callgraph. The graph is a directed graph. We can understand the caller-callee
relationsip with callgraph. For python, we can use `pycallgraph` to generate
the callgraph.

## Look closer

From the profiler results, we found the same function `fibonacci_v1` is called
for so many times. To get `F(n)`, we need to compute `F(n-1)` and `F(n-2)`
first. In fact, `F(n-1)` requires `F(n-2)` too!. They are overlapping! If you
remember the *egg-dropping problem*, we showed that using `memorization` can
help a lot. Let's implement a super simple cache.

```
# Take a look python3 LRU cache too!
# https://docs.python.org/3/library/functools.html#functools.lru_cache

class memorize(object):
  def __init__(self):
    self.cache = {}

  def __call__(self, fn):
    from functools import wraps
    @wraps(fn)
    def wrapped(*args):
      if args not in self.cache:
        #logging.debug('not cached. key = {}'.format(args))
        self.cache[args] = fn(*args)
      return self.cache[args]
    return wrapped


@memorize()
def fibonacci_v1b(n):
  if n == 0:
    return 0

  if n == 1:
    return 1

  return fibonacci_v1b(n-1) + fibonacci_v1b(n-2)
```


We trade memory space for computation time. After that, we can sucessfully
compute `F(30)` or `F(50)` quickly because we eliminate the reduntant
computations. How about `F(1000)`?  Well we still can't get it. The program
received an error message:

```
RuntimeError: maximum recursion depth exceeded
```

Remember the `stack` thing we discussed a few minutes ago? When the recursion
is too _deep_, we runs out of memory to push the current state into the stack.
The program will get this exception. (who throw this exception anyways?) Looks
like there is something at the fundamental level that blocks our path to
success. Let's go back to our source code to see what we can find. We used
recursion to compute the Fibonacci number (as the definition says). One of the
differences between scientist and engineer is that the latter one also cares
about the implementation aspect.

One little trick for finding Fibonacci number and some recursive functions is
that we can turn the recursion to iteration (e.g. a `for-loop`). Technically
speaking, computer scientists studied this recursion to iteration
transformation for years. Questions like "can all recursion functions be converted and
how?" are somewhat addressed. See
[this](https://stackoverflow.com/questions/931762/can-every-recursion-be-converted-into-iteration).
In general, some high level languages do the conversion for you
*AUTOMAGICALLY*. However, Python does not come with this feature. So it is up
to us to convert it manaully. (Sometimes, the code/algo is easier to understand
with the recurive form.)


## Iteractive implementation

So here is the iteractive way to find Fibonacci number.

```
def fibonacci_v2(n):
  f0 = 0
  f1 = 1
  if n == 0:
    return f0
  if n == 1:
    return f1
  for i in xrange(2, n + 1):
    f0, f1 = f1, f0 + f1
  return f1
```

It might not be the most elegant solution but it does much better than the
naive implementation. How good it is? First, it can handle `F(50)` in a blink
of an eye. It also uses way less memory. (TODO: How do I know that besides
reading the code?) In this case, it uses constanst memory space (`O(1)` memory
complexity) and in term of computation complexity, it is `O(n)`. So, can we do
`F(1000)` with this implementation? The answer is, of course, a *Yes*. Here is
the profiler output for getting the first 1000-th Fibonacci number.

```
         2484 function calls in 0.070 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1001    0.050    0.000    0.050    0.000 main.py:15(fibonacci_v2)
        1    0.007    0.007    0.014    0.014 __init__.py:24(<module>)
        1    0.004    0.004    0.070    0.070 main.py:1(<module>)
        1    0.003    0.003    0.005    0.005 collections.py:11(<module>)
        1    0.002    0.002    0.002    0.002 heapq.py:31(<module>)
     1001    0.001    0.000    0.001    0.000 {method 'format' of 'str' objects}
```

## Why not push the limit? Where is our limit?

In fact, there is a `O(log n)` method. See
[Wikipedia](https://en.wikipedia.org/wiki/Fibonacci_number#Matrix_form). You
should be able to prove it with MI... Let's assume the wiki and the Maths are
true. We get two identities from the matrix form and allow us to derive `O(log
n)` algo.

## Next step?

Let's take a look what memory profiler can do.

# Updated `main.py`

```
#!/usr/bin/env python27

import logging
logging.basicConfig(level=logging.DEBUG)

def fibonacci_v1(n):
  '''The naive recursive implementation. It starts not working when n is around
  30-40.'''
  if n == 0:
    return 0

  if n == 1:
    return 1

  return fibonacci_v1(n-1) + fibonacci_v1(n-2)


class memorize(object):
  '''A simple cache.'''
  def __init__(self):
    self.cache = {}

  def __call__(self, fn):
    from functools import wraps
    @wraps(fn)
    def wrapped(*args):
      if args not in self.cache:
        #logging.debug('not cached. key = {}'.format(args))
        self.cache[args] = fn(*args)
      return self.cache[args]
    return wrapped


@memorize()
def fibonacci_v1b(n):
  '''Memorize the previous result to reduce function calls.'''
  if n == 0:
    return 0

  if n == 1:
    return 1

  return fibonacci_v1b(n-1) + fibonacci_v1b(n-2)


def fibonacci_v2(n):
  ''' An iterative implementation. Should be faster and use constant memory
  compared to the naive recursive implementation.'''
  f0 = 0
  f1 = 1
  if n == 0:
    return f0
  if n == 1:
    return f1
  #logging.debug((f0, f1))
  for i in xrange(2, n + 1):
    f0, f1 = f1, f0 + f1
    #logging.debug((f0, f1))
  return f1


examples = [0,1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,
     1597,2584,4181,6765,10946,17711,28657,46368,75025,
      121393,196418,317811,514229,832040,1346269,
       2178309,3524578,5702887,9227465,14930352,24157817,
        39088169,63245986,102334155]

test_cases = zip(range(len(examples)), examples)

if __name__ == '__main__':
  import os
  fn = globals()['fibonacci_' + os.getenv('F', 'v1')]
  if os.getenv('ENV') == 'TEST':
    # for testing the correctness of the implementations.
    for i, tc in enumerate(test_cases):
      try:
        args, expected = tc[:-1], tc[-1]
        assert fn(*args) == expected
        logging.debug('Test case #{} passed'.format(i))
      except AssertionError:
        logging.error((args, expected))
  else:
    n = int(os.getenv('N', '10'))
    start = int(os.getenv('S', '0'))
    assert start <= n
    for x in xrange(start, n + 1, 1):
      print 'F({}) = {}'.format(x, fn(x))
```
