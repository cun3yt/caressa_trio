# Caressa Main Repository

Welcome to Caressa's code repository. Currently it includes two main repositories in this central location:

0. Django codebase including 
    * Data (ORM) models
    * HTTP endpoints for Voice devices (currently only Alexa)
    * REST API for mobile clients
0. Quasar codebase for targeting iOS and Android builds

Please note that this file is super shaky, please consider contributing it if you see something dramatically wrong. Thanks for your patience!

# Django Codebase

## Installation

This setup is written for Mac OS.

0. Install PostgreSQL (Current running version for the product: 9.6)
    * Install Homebrew if you don't have already: https://brew.sh/
    * Run `brew cask install postgres`
    * Postgres is a visual postgreSQL server
    * You can start/stop from the toolbar
0. Install Postico (visual database client)
    * Install Homebrew if you don't have already: https://brew.sh/
    * `brew cask install postico`
0. PyEnv, Python and VirtualEnv Setup
    * Install Homebrew if you don't have already: https://brew.sh/
    * Install Pyenv for python environment management:
        * `brew update`
        * `brew install pyenv`
        * For any problems refer to [Pyenv's wiki](https://github.com/pyenv/pyenv/wiki).
    * Install Python3.6.4 through Pyenv:
        * `pyenv install 3.6.4`
    * Install Virtualenv for development environment isolation:
        * `brew install pyenv-virtualenv`
    * Create a virtual environment with Python3.6.4:
        * `pyenv virtualenv 3.6.4 caressa`
0. Activate Virtual Environment
    * Run `source ~/.pyenv/versions/caressa/bin/activate`
0. Installing Requirements
    * Go to project root
    * Run `pip install -r requirements`
0. Run Database Migrations
    * Go to project root
    * Run `./manage.py migrate`
0. Export these environment variables. You may consider using `direnv` for project-based environment variables' management:
    * ENV set to 'dev': `export ENV='dev'`
    * ENV_KEY set to some long string: `export ENV_KEY='some-long-random-string'`
    * DATABASE_URL set to the local database instance, e.g.: `export DATABASE_URL='postgres://cuneyt:@localhost:5432/caressa_django'`
0. Development Server
    * Run `./manage.py runserver 9900`
    * Hit: `http://localhost:9900/act/actions/` If you see a meaningful page that's great. If not try to solve the problem and if you cannot get some help from other folks.
    * For easier debugging: JetBrain IDEs providing Django Run/Debug configuration which eases the pain.

# Quasar Codebase

[Quasar](https://quasar-framework.org/) is a VueJS-based framework that provides hybrid mobile apps, web apps and more with the same codebase.

## Installation

This setup is written for Mac OS.

0. Install [`node`](https://nodejs.org/en/) if you don't have it already. If you have a super old version of node consider updating it. You may consider using `homebrew` for the installation/update.
0. Go to `q_client` folder
0. Install `vue-cli` globally: `npm install -g vue-cli`
0. Run `npm install`
0. Start dev server: `quasar dev`. If build is successful hit to `http://localhost:8080/main/health-numbers`. If you see meaningful app-like looking page you're done. Congrats.

# Setting Alexa Skill for Development

In order to do development against an Alexa skill each developer will need one Alexa project initiated on Amazon servers. The steps to get that done:

0. Create an Amazon developer account if you haven't already: https://developer.amazon.com/alexa/console
0. ...More to come...
