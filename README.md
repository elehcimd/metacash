# MetaCash

MetaCash lets you import, label, manipulate, and analyze historical transactions from multiple financial accounts
with the superpowers of Pandas, Jupyter, ipywidgets, and matplotlib.

With MetaCash you can:

* Load transactions from bank statements, credit, debit, prepair, and online accounts
* Maintain a complete and consistent archive of your historical transactions
* Label transactions with regular expression and handle different views such as "personal" and "freelance"  
* Explore transactions with an interactive web dashboard and as data frames for for deep dives
* Manipulate transactions safely with *transaction frames*

## Project status

* Used extensively by author
* Documentation needs improvement
* Contributions welcome! see *Contributing* section

## Screenshots

### Selecting target period

![Selecting target period](/screenshots/s1.png?raw=true)

### Exploring transactions

![Exploring transactions](/screenshots/s2.png?raw=true)

## Transaction frames

Transaction frames are Pandas data frames where each row represents a transaction with these columns:

* `timestamp`: timestamp of transaction
* `balance`: rolling balance
* `amount`: amount of transaction
* `currency`: currency of transaction
* `description`: description of transaction
* `type`: type of record (`t`: regular, `ib`: initial balance, `fb`: final balance)
* `label.category`: transaction category

The first and records are of type `ib` and `fb`, respectively. The other intermediate records are of type `t`.
The first and last records, as well as the rolling `balance`, ensure consistency and completeness with merge operations.

## Setting up the local environment

### MacOS

Install `pyenv`

First:

```
brew update
brew install pyenv
brew install pyenv-virtualenv
```

Add to `~.zshrc`:

```
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
  export PYENV_VIRTUALENV_DISABLE_PROMPT=1
fi

if which pyenv-virtualenv-init > /dev/null; then eval "$(pyenv virtualenv-init -)"; fi
```

* Install a specific version of Python: `pyenv install 3.6.10`
* Create virtualenv: `pyenv virtualenv 3.6.10 metacash`
* Activate virtualenv: `pyenv activate metacash`
* Update pip: `pip install --upgrade pip`
* Install packages: `pip install -r requirements.txt`

### Fabric commands

* `fab build`: build image
* `fab start`: start image
* `fab kill`: terminate container
* `fab test-pep8`: run PEP8 test
* `fab test`: run all tests

To install `ipywidgets`:

```
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
apt install npm build-essential
jupyter labextension install @jupyter-widgets/jupyterlab-manager@2.0
```

# Contributing

1. Fork it
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Create a new Pull Request