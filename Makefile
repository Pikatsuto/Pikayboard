VBIN = venv/bin/python

all: start

clean:
	rm -rf venv
	rm -rf *.egg-info
	rm -rf *__pycache__
	sudo rm -rf /usr/bin/pikayboard
	sudo rm -rf /usr/share/applications/pikayboard.desktop

$(VBIN):
	python -m venv venv
	chmod +x venv/bin/activate
	./venv/bin/activate
	pip install -e .
	sudo chmod +x /usr/bin/pikayboard
	sudo chmod +x /usr/share/applications/pikayboard.desktop

start: $(VBIN)
	python pikayboard

.PHONY: clean all start