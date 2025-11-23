phony: run, run_dev

run_dev:
	TESTING="true" \
	FLASK_DEBUG="true" \
	uv run flask run

run:
	uv run flask run
