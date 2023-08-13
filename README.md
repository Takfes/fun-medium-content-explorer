# REPO BASICS

## HOW TO USE

1. how to create virtual env : `virtualenv venv`
2. how to activate the env : `. venv/bin/activate`
3. how to install the package : `pip install -e .`
4. how to deactivate the env : `deactivate`
5. `docker-compose -f docker-compose-<enter file id here>.yaml up -d`
6. `docker-compose -f docker-compose-<enter file id here>.yaml down`

> run `pip freeze | grep -v "^\-e" > requirements.txt` when **new packages are installed**, to include them in the `requirements.txt`. these will build everytime you `pip install -e .`

## NEXT STEPs

- enable dvc tracking - getting errors so far
- enable dvc pipeline - get updates > crawl > push in the db
- enable huggingface models for multilabel classification
