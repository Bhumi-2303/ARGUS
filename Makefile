.PHONY: setup api web test demo clean

setup:
	pip install -e .[dev,test]

api:
	uvicorn argus.api.main:app --host 0.0.0.0 --port 8000 --reload

web:
	cd web && npm run dev

test:
	pytest tests/

demo:
	python scripts/start_demo.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
