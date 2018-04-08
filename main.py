#!/usr/bin/env python27

import logging
logging.basicConfig(level=logging.DEBUG)

def fibonacci_v1(n):
  if n == 0:
    return 0

  if n == 1:
    return 1

  return fibonacci_v1(n-1) + fibonacci_v1(n-2)


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


def fibonacci_v2(n):
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
