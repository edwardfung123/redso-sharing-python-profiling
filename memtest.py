#!/usr/bin/env python27
# -*- coding: utf-8 -*-

import gc
gc.disable()

def myprofile(fn):
  def mywrap(*args, **kwargs):
    from guppy import hpy
    hxx = hpy()
    heap = hxx.heap()
    print 'before function call "%s"' % fn.__name__
    old = (heap.count, heap.size)
    ret = fn(*args, **kwargs)
    print 'after function call'
    heap = hxx.heap()
    new = (heap.count, heap.size)
    print 'original objects = %d, memory %d bytes' % old
    print 'new objects = %d, memdiff = %d bytes (around %.2f MB)' % (new[0]-old[0], new[1] - old[1], (new[1] - old[1]) / 1024.0 / 1024.0)
    return ret
  return mywrap

@myprofile
def to_csv_v1(members):
  from guppy import hpy
  hxx = hpy()
  heap = hxx.heap()
  old = (heap.count, heap.size)
  #s = u''
  #for m in members:
  #  s += u', ' + m if s else m
  import btwording
  s = btwording.WORDING_DICTS['zh-Hant'].values()[0]
  heap = hxx.heap()
  new = (heap.count, heap.size)
  print 'new objects = %d, memdiff = %d bytes (around %.2f MB)' % (new[0]-old[0], new[1] - old[1], (new[1] - old[1]) / 1024.0 / 1024.0)
  return s

@myprofile
def dummy():
  pass

def to_csv_v2(members):
  return u', '.join(members)

if __name__ == '__main__':
  from guppy import hpy
  hxx = hpy()
  heap = hxx.heap()
  print heap
  print '======'
  #import pdb; pdb.set_trace()
  members = map(str, range(1000))
  heap = hxx.heap()
  print heap
  print '======'

  x = dummy()
  x = to_csv_v1(members)
  #print x
  print hxx.iso(x)
  heap = hxx.heap()
  print heap

  #x = to_csv_v1(members).encode('utf-8')
  #print hxx.iso(to_csv_v2(members).encode('utf-8'))
  #heap = hxx.heap()
  #print heap

