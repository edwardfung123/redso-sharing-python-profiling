# use F=v2 to select method
# use N=1000 to change the number of Fibonacci numbers to be computed.
default: profile

profile:
	#F=v2 N=20 python -m cProfile -s time main.py
	python -m cProfile -s time main.py

callgraph:
	pycallgraph graphviz -- main.py
