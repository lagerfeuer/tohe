# tohe
tohe - the TODO list helper

# Development

## Setup
```sh
poetry install
```

## Unit tests
```sh
poetry run pytest --cov=tohe/ tests/
# or
poetry run python -m pytest --cov=tohe/ tests/
```

### mypy
```sh
poetry run mypy tohe/
# or
poetry run python -m mypy tohe/
```


## TODO
- [ ] Add Bash and Zsh completion
- [ ] Add docstrings
- [ ] How should headers be treated?
  * First line is header (i.e. `# header line` or just `header line`)
  * Tag line is header (i.e. `header: header line`)
- [ ] If using a header line, do the same with tags (i.e. `tags: main,todo,test`)
- [ ] Build a web server around it for easier reading and editing
- [ ] Add fzf support for searching
- [ ] Add ncurses TUI
