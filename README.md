# REPO BASICS

## HOW TO USE

1. how to create virtual env : `virtualenv venv`
2. how to activate the env : `. venv/bin/activate`
3. how to install the package : `pip install -e .`
4. how to deactivate the env : `deactivate`

> run `pip freeze | grep -v "^\-e" > requirements.txt` when **new packages are installed**, to include them in the `requirements.txt`. these will build everytime you `pip install -e .`

> run the `pipeline.sh` to trigger the entire pipeline

## NEXT STEPs

- enable vector database for embeddings
- enable dvc tracking - getting errors so far
- enable dvc pipeline - get updates > crawl > push in the db
- enable huggingface models for multilabel classification
