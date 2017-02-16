

CMD=clingo -n 0 data.lp


l: sofa
sofa:
	$(CMD) sofa.lp

j: simple
simple:
	$(CMD) simple.lp


pyj:
	python3 navigation.py

pyg:
	python3 gui.py
