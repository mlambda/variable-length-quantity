all:
	pytest
	mutmut run --paths-to-mutate vlq.py

.PHONY: all
