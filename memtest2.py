import gc
gc.disable()
from memory_profiler import profile
from memory_profiler import memory_usage

def my_func(data):
  s = u''
  for d in data:
    s += u'\n' + d if s else d
  return s

def my_func2(data):
  s = u'\n'.join(data)
  return s

@profile
def main():
  l = 50000
  data = 'a' * l
  #data2 = 'a' * (l - 1)
  import btwording
  del btwording
  import sys
  print sys.getsizeof(data)
  prof, ret2 = memory_usage((my_func2, (data, )), retval=True)
  print sys.getsizeof(ret2) / 1024.0 / 1024.0
  print prof
  del ret2
  prof, ret1 = memory_usage((my_func, (data, )), retval=True)
  print prof
  del ret1
  del data


if __name__ == '__main__':
  main()
