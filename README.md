### HOW TO USE

1. how to create virtual env : `virtualenv venv`
2. how to activate the env : `. venv/bin/activate`
3. how to install the package : `pip install -e .`
4. how to deactivate the env : `deactivate`

> run `pip freeze | grep -v "^\-e" > requirements.txt` when **new packages are installed**, to include them in the `requirements.txt`. these will build everytime you `pip install -e .`

### The MEDIUM-SCRAPING module structure

- `setup.py` defines the `scraping` module.
- inside `scraping` there may be several submodules, each with its own purpose.
- one such model is `medium`.
- `scraping/medium/main.py` encapsulates the main functionality to poll the medium-api to obtain all the articles from a medium reading list. all the configuration is in `scraping/medium/config.py`.
- `scraping/medium_runner.py` simply invokes `scraping/medium/main.py` and runs across the list of medium readin lists.
- to run this `python scraping/medium_runner.py`

### The MEDIUM-SCRAPING CLI structure

- `setup.py` also enables the `scrape` `entry_points`, which is a CLI interface.
- this accepts the `<module> e.g. medium` as an argument to call the respective module, in this instance `scraping\medium\main.py` under the hood.
- whatever argument provided after the `<module>` will be propagated to `scraping\medium\main.py:default`, as suggested by `"scrape = scraping.main:default",`.
- to run medium-cli version : `scrape medium <collection_key> <limit>`.

### NEXT STEPs

- make scraper for medium articles
- scrape text out of links w/ queue manager
- merge with python-medium-nlp directory
- grab items from scraping-w/ scrapy training
- store parsed results - redis or mongo/mongo-atlas
- consider demo helm & docker-compse
- create streamlit
- jaal to represent objects or neo4j
- multiclass classification of items - huggingface
- chat gpt and vector database
- dagshub and dvc
- poetry, cookiecutter, makefile, (.vscode, setup.py)
- enable tests - pytests
