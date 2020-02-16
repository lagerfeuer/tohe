# tohe
tohe - the TODO list helper

# Install
```sh
pip3 install tohe
```

# Usage
## General usage information
### Tags
Tags can be supplied via `-t TAG1 TAG2`.
Operations that add tags also expect tags in the form `-t TAG1 TAG2`.
Operations that remove tags work similar, but expect the flag `-r`, like `-r REMOVETAG1 REMOVETAG2`.

## Supported operations:
* **add**
```sh
tohe add [-t TAG [TAG ...]] [CONTENT]
```
If `CONTENT` is not provided, `$EDITOR` will be opened to get content for the entry.

* **list**
```sh
tohe list [-t TAG [TAG ...]]
```
*Not supported yet*: Tag filtering

* **edit**
```sh
tohe edit [-t TAGS [TAGS ...]] [-r RTAGS [RTAGS ...]] ID
```

* **search**
```sh
tohe search [-w] TERM
```
`-w|--wildcard` enables the use of `*` and `?` wildcards

* **delete**
```sh
tohe delete ID
```

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
- [ ] Add support for currently unsupported options like `-db` and `--loglevel`.
- [ ] Add Bash and Zsh completion
- [ ] Add docstrings
- [ ] Maybe enable tag editing in the editor (i.e. `tags: main,todo,test`)
- [ ] Build a web server around it for easier reading and editing
- [ ] Add fzf support for searching
- [ ] Add ncurses TUI
