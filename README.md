# Caressa Main Repository

Welcome to Caressa's code repository. Currently it includes two main repositories in this central location:

1. Django codebase including 
    * Data (ORM) models
    * HTTP endpoints for Voice devices (currently only Alexa)
    * REST API for mobile clients
1. Quasar codebase for targeting iOS and Android builds

Please note that this file is super shaky and consider contributing if you see something dramatically wrong. Thanks for your patience!

# Django Codebase

## Installation

This setup is written for Mac OS.

1. Install PostgreSQL (Current running version for the product: 9.6)
    * Install Homebrew if you don't have already: https://brew.sh/
    * Run `brew cask install postgres`
    * Postgres is a visual postgreSQL server
    * You can start/stop from the toolbar
1. Install Postico (visual database client)
    * Install Homebrew if you don't have already: https://brew.sh/
    * `brew cask install postico`
    * Click `Initialize` button
1. PyEnv, Python and VirtualEnv Setup
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
        * Add the following lines to profile file:
            * `eval "$(pyenv init -)"`
            * `eval "$(pyenv virtualenv-init -)"`
1. Activate Virtual Environment
    * Run `source ~/.pyenv/versions/caressa/bin/activate`
1. Installing Requirements
    * Go to project root
    * Run `pip install -r requirements`
1. Export these environment variables. You may consider using `direnv` for project-based environment variables' management:
    * ENV set to 'dev': `export ENV='dev'`
    * ENV_KEY set to some long string: `export ENV_KEY='some-long-random-string'`
    * DATABASE_URL set to the local database instance, e.g.: `export DATABASE_URL='postgres://cuneyt:@localhost:5432/caressa_django'`
1. Run Database Migrations
    * Go to project root
    * Run `./manage.py migrate`
1. Development Server
    * Run `./manage.py runserver 9900`
    * Hit: `http://localhost:9900/act/actions/` If you see a meaningful page that's great. If not try to solve the problem and if you cannot get some help from other folks.
    * For easier debugging: JetBrain IDEs providing Django Run/Debug configuration which eases the pain.

## Specific to PyCharm & Possibly IntelliJ

* PyCharm's debug server is extremely useful for debugging. In order to use it is needed to specify the Python interpreter properly: The one that is available in the virtual environment. It can be set under `PyCharm > Preferences > Project: xxx > Project Interpreter > Project Interpreter`
* Make sure that the IDE is set properly for Django: Go to `PyCharm > Preferences > Language & Frameworks > Django`. Mark `Enable Django Support` checked, set the "Django Project Root" to the folder where `settings.py` file is in (absolute url of the directory), set "Settings" to `settings.py` (just file name), specify the Manage script to the absolute url of `manage.py` file.
 

# Quasar Codebase

[Quasar](https://quasar-framework.org/) is a VueJS-based framework that provides hybrid mobile apps, web apps and more with the same codebase.

## Installation

This setup is written for Mac OS.

1. Install [`node`](https://nodejs.org/en/) if you don't have it already. If you have a super old version of node consider updating it. You may consider using `homebrew` for the installation/update.
1. Install `vue-cli` globally: `npm install -g vue-cli`
1. Go to `q_client` folder
1. Run `npm install`
1. Start dev server: `quasar dev`. If build is successful hit to `http://localhost:8080/main/health-numbers`. If you see meaningful app-like looking page you're done. Congrats.

## IOS Build


1. You need to sign your development team in project. I think there is a better way to do that but I did it like this, first open the project in Xcode and choose the development team as yourself manually in Xcode.
1. q_client/src/plugins/resource.js 
```
app.hosts = {
    rest:'http://127.0.0.1:9900'
}
``` 
changed to 
```
app.hosts = {
    rest:'https://yourserver.serveo.net'
}
```
where you are serving your REST globally. Check it out [Serveo](serveo.net). Your phone need to be able to reach that url so it is better to have something global. 
1. You need to config CORS: Caressa > settings.py > CORS_ORIGIN_WHITELIST add your IP that is trying to reach resources you can see in debugger configured at Debugging your IOS Build section.
1. Start dev server: `quasar dev -m cordova -T ios`. If build is successful application will automatically open in your phone. Well in most cases..
1. If any problem occurs you can check debugging feature.  


## Debugging Your IOS Build.  
1. IOS Device: Go to Settings > Safari > Advanced > Enable : Web Inspector / Javascript
1. Safari Browser : Preferences > Advanced > Enable : Show Develop Menu Bar
1. Safari Browser : Menu Bar >  Develop >  Your IOS Device > Index is your debugger

# Setting Alexa Skill for Development

In order to do development against an Alexa skill each developer will need one Alexa project initiated on Amazon servers. The steps to get that done:

1. Create an Amazon developer account if you haven't already: https://developer.amazon.com/alexa/console
1. Create a skill named "caressa-dev" as a custom skill
1. Open JSON editor on Alexa web dashboard and insert the seed skill info (ask to a coworker if it is not available somewhere yet).
1. Alexa skill expects an HTTPS endpoint to reach to the skill. In order to make it work on the local machine you need to create a world-wide accessible HTTP server. There are two alternatives that we have identified so far without going through lots of configurations for firewalls etc:
    * Install `ngrok` (available on Homebrew as a cask: `brew cask install ngrok`) and run it: 
    @todo ... specs will be here... 
    The free account generates a different URL for each run.
    * Create reverse SSH for global-local server via service Serveo. Example run is like this: `ssh -R letatio.serveo.net:80:localhost:9900 serveo.net`. The good thing about Serveo is that it tries to stick with the URL based on the IP and it is for free. It is not always available so keep `ngrok` in mind, too.
1. Once you have worldwide accessible HTTP server you'll need to tell it to the Alexa on its web dashboard, it must be under endpoints.
1. Open the test tab on Alexa web dashboard and write `open Caressa` to test the connection to your local machine.

## Setting Pusher For Live Updates on Mobile App
* Export these environment variables. You can put these in `.envrc` if you are using direnv.
    * PUSHER_APP_ID set to 'some_app_id': `export PUSHER_APP_ID='some_app_id'`
    * PUSHER_KEY set to 'some_pusher_key': `export PUSHER_KEY='some_pusher_key'`
    * PUSHER_SECRET set to 'some_pusher_secret': `export PUSHER_SECRET='some_pusher_secret'`
    * PUSHER_CLUSTER set to 'us2': `export PUSHER_CLUSTER='us2'`
    * Don't forget to add these environment variables into pycharm if you are using it.
    