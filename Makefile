VBIN = venv/bin/python

all: start

clean:
	rm -rf venv
	rm -rf *.egg-info
	rm -rf *__pycache__

$(VBIN):
	python -m venv venv
	chmod +x venv/bin/activate
	./venv/bin/activate
	pip install -e .

start: $(VBIN)
	python pikayboard

.PHONY: clean all start