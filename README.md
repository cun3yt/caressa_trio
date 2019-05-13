[![Build Status](https://semaphoreci.com/api/v1/projects/feec7071-453b-4a9f-b392-8669d5277617/2504119/badge.svg)](https://semaphoreci.com/caressa/caressa_trio)

# Caressa Main Repository

Welcome to Caressa's code repository. Currently it includes two main repositories in this central location:

1. Django codebase including
    * Data (ORM) models
    * HTTP endpoints for Caressa hardware
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
    * VIRTUAL_ENV_PATH set to the virtual environment path that is in use, e.g.: `export VIRTUAL_ENV_PATH='/Users/cuneyt/.pyenv/versions/caressa'`
    * PROJECT_ROOT set to the project root, e.g.: `export PROJECT_ROOT='/Users/cuneyt/Work/caressa'`
    * HOSTED_ENV set to the serveo/ngrok or which environment you serve your dev server for external client development (e.g. senior hardware): `export HOSTED_ENV='https://yourserver.serveo.net/'`
    * AWS_ACCESS_KEY_ID set to active AWS access key id.
    * AWS_SECRET_ACCESS_KEY set to active AWS secret access key id.
    * MEDIA_BUCKET set to active s3 bucket on AWS.
    * API_URL: base api URL (without slash at the end), e.g. "http://localhost:8000"
    * WEB_BASE_URL: base web app URL (without slash at the end), e.g. "http://localhost:8000"
    * Oauth2 Credentials (refer to oauth docs.)
        * WEB_CLIENT_ID: Oauth2 client_id is a public identifier for apps.
        * WEB_CLIENT_SECRET: Oauth2 client_secret known only to the application and the authorization server.
    * Email backend SMTP setup (e.g. refer to mailgun account)
        * EMAIL_HOST: SMTP server hostname.
        * EMAIL_PORT
        * EMAIL_HOST_USER
        * EMAIL_USE_TLS
        * EMAIL_HOST_PASSWORD
    * SMS backend setup (e.g. refer to twilio account)
        * TWILIO_ACCOUNT_SID
        * TWILIO_AUTH_TOKEN
        * TWILIO_PHONE_NUMBER
    * Dataplicity for device connectivity/status check
        * DATAPLICITY_USER: user email address
        * DATAPLICITY_PASSWD: user password
    * Google Cloud Credentials (based on [this article](https://simpleit.rocks/apis/google-cloud/using-google-cloud-with-heroku/)):
        * `GOOGLE_APPLICATION_CREDENTIALS_RAW` the content of the JSON file. You can put a line similar to 
        the one below to your `.envrc`:
        `export GOOGLE_APPLICATION_CREDENTIALS_RAW="$(< your-google_key-file.json)"`
        * The credentials can be set as the content of the file on the server, e.g. for Heroku, 
        `heroku config:set GOOGLE_APPLICATION_CREDENTIALS="$(< credentials.json)"`
    * SENTRY_DSN 
        * Get an invite for Sentry
        * Head [Sentry Caressa Page](https://sentry.io/settings/caressa/projects/)
        * Create new project as django and you will have the DSN 
        
1. Javascript codebase 
    * JS codes are based on VueJS, with application definitions under /static/javascript/pages/
    * You need to setup webpack to compile the Vue files:
        * Install `npm` if you haven't done already.
        * Install npm package: `npm install`
        * Run webpack builder which is an npm run script (see in package.json): `npm run build`. You need to run it every time you make a change in Vue files, related JS files and html templates. It may be wise to setup a file watcher to run it, see "IDE-Related Workflow" section below. 

1. Run Database Migrations
    * Go to project root
    * Run `./manage.py migrate`
1. Development Server
    * Run `./manage.py runserver 9900`
    * Hit: `http://localhost:9900/act/actions/` If you see a meaningful page that's great. If not try to solve the problem and if you cannot get some help from other folks.
    * For easier debugging: JetBrain IDEs providing Django Run/Debug configuration which eases the pain.
1. Running Tests Before Push via Git Push Hook
    * Go to `.git/` folder.
    * If you already have a `hooks` folder delete it.
    * Symlink `hooks` to `../scripts/githooks/`, from project root:
    ```bash
    ln -s -f ../scripts/githooks/ .hooks
    ```
    * Now every time you try to push your Python changes in commits, tests under version control will be triggered. If tests run and there is any failure the push will not be executed. Please note:  
        * If there is not Python change tests will not be executed.
        * If you have any tests that are not committed yet they will not be executed.

## IDE-Related Workflow (Specific to PyCharm & Possibly IntelliJ)

* PyCharm's debug server is extremely useful for debugging. In order to use it is needed to specify the Python interpreter properly: The one that is available in the virtual environment. It can be set under `PyCharm > Preferences > Project: xxx > Project Interpreter > Project Interpreter`
* Make sure that the IDE is set properly for Django: Go to `PyCharm > Preferences > Language & Frameworks > Django`. Mark `Enable Django Support` checked, set the "Django Project Root" to the folder where `settings.py` file is in (absolute url of the directory), set "Settings" to `settings.py` (just file name), specify the Manage script to the absolute url of `manage.py` file.
* You can setup a file watcher to bundle static files. Go to `PyCharm > Preferences > Tools > File Watchers`. Add watchers for JS and Vue files (possibly two separate files) to run `npm run build`.

# Quasar Codebase

[Quasar](https://quasar-framework.org/) is a VueJS-based framework that provides hybrid mobile apps, web apps and more with the same codebase.

## Installation

This setup is written for Mac OS.

1. Install [`node`](https://nodejs.org/en/) if you don't have it already. If you have a super old version of node consider updating it. You may consider using `homebrew` for the installation/update.
1. Install `vue-cli` globally: `npm install -g vue-cli`
1. Go to `q_client` folder
1. Run `npm install`
1. Copy & paste the file `q_client/src/.env.template.js` as `q_client/src/.env.js`, update the necessary variables, similar to environment variables.
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
1. You need to config CORS_ORIGIN_WHITELIST on your .envrc. Add your IP that is trying to reach resources. You can see the IP in debugger which is configured at Debugging your IOS Build section.
1. Start dev server: `quasar dev -m cordova -T ios`. If build is successful application will automatically open in your phone. Well in most cases..
1. If any problem occurs you can check debugging feature.  
1. We need to use legacy build option for Cordova built. To do that in XCode open your project. File > Workspace Settings > Build System choose Legacy Build System
1. npm i cordova-plugin-ios-microphone-permissions


## Debugging Your IOS Build.  
1. IOS Device: Go to Settings > Safari > Advanced > Enable : Web Inspector / Javascript
1. Safari Browser : Preferences > Advanced > Enable : Show Develop Menu Bar
1. Safari Browser : Menu Bar >  Develop >  Your IOS Device > Index is your debugger

## Setting Pusher For Live Updates on Mobile App
* Export these environment variables. You can put these in `.envrc` if you are using direnv.
    * PUSHER_APP_ID set to 'some_app_id': `export PUSHER_APP_ID='some_app_id'`
    * PUSHER_KEY set to 'some_pusher_key': `export PUSHER_KEY='some_pusher_key'`
    * PUSHER_SECRET set to 'some_pusher_secret': `export PUSHER_SECRET='some_pusher_secret'`
    * PUSHER_CLUSTER set to 'us2': `export PUSHER_CLUSTER='us2'`
    * Don't forget to add these environment variables into pycharm if you are using it.

## Testflight Testing & iOS App Store publish
* Uploading app for testing is can be done with XCODE:
    * In order to release a new build, you need to increment at least build number on XCODE before archive / upload. Version number can stay same.
    * XCODE > Product > Archive > Click
    * After clicking it will build the app and menu will show up.
    * Click latest build and click Distribtue App button on the right.
    * Select iOS App Store > Upload > Select Both and Next > Automatically Manage Signing > Last Checks
    * Upload button will show up if everything is correct.
    * Click Upload.
* Head to  your developer account at apple.com:
    * New build takes a little bit time to show up on developer panel even everything goes smoothly.
    * Your app panel is at https://appstoreconnect.apple.com > My Apps
    * After selecting your recently built app click Testflight Tab
    * To publish the new version to test users click App Store Connect Users on left panel.
    * Click Builds Tab > If there is any warnings click and solve it. 
    * Finally app will become available to test
    * Internal testing is limited to 25 person.

## How Message Queue Process Script Works
* Relative location of the script : scripts/message_queue_process_script.py
* Script has 3 worker function inside, these are:
    * audio_worker: This one takes audio from s3 (recorded and upload by mobile app) format it to mp3 if needed and pushes its URL with pusher to client.
    * text_worker: This one takes text message from app uses tts_to_s3 function and pushes its URL with pusher to client.
    * personalization_worker: When senior preferences changed it will make the changes and will notify in Caressa Hardware with TTS.
* You can run the script with this command. `./manage.py runscript  message_queue_process_script` It has infinite loop inside with 2 sec sleep time.

## Tests and Coverage Report
* Run `coverage run manage.py test` to generate `.coverage` file. Optionally, you can run a specific
test by adding the path of the test to the end of the command: `coverage run manage.py test utilities.tests`. 
Event specific unittest class can run: `coverage run manage.py test utilities.tests.TestStatisticsUniformDistribution` 
* See the test coverage report (interprets `.coverage` file): `coverage report`
* See `.coveragerc` for default configuration. You can also use command line arguments to change behavior

## Email Templates
* Email templates are planned as tables as it is the most convenient way.
* There is two main part in the templates. Head and Body.
    * Head keeps styles
    * Body keeps content inside table/tr/td HTML tags.
* For more info which is used https://github.com/seanpowell/Email-Boilerplate
