# todd
Todd, the TODO list helper

# Development

## Setup
```sh
poetry install
```

## Unit tests
```sh
poetry run pytest --mypy --cov=todd/ tests/
# or
poetry run python -m pytest --mypy --cov=todd/ tests/
```


## TODO
- [ ] Add docstrings
- [ ] How should headers be treated?
  * First line is header (i.e. `# header line` or just `header line`)
  * Tag line is header (i.e. `header: header line`)
- [ ] If using a header line, do the same with tags (i.e. `tags: main,todo,test`)
- [ ] Build a web server around it for easier reading and editing
- [ ] Add fzf support for searching
- [ ] Add ncurses TUI