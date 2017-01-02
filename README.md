# Web UI for Robinhood

This project aims to be an alternative, or supplamental, web interface for 
the popular Robinhood Financial trading application. It uses unpublished 
Robinhood APIs so use with caution. It's built with HTML5, AngularJS, and Python.

The UI can be hosted locally for security reasons and supports both 
username & password authentication as well as direct token authentication. There 
is also no database in use here and local browser storage is used for persistence. 


## Getting Started
### Building the API service

**Prerequisites**

* [Python 2.x](https://www.python.org/downloads/)

**Install guide**

Change directories into the */api/* project folder. Then simply 
install the project requirements by running `pip install -e requirements`

This will install Flask(-RESTful) which is what the project uses to create 
the API service. That's all of the requirements needed. 

To run the service, execute ```python api.py```

You should now have an API service running on default port 5000. 

### Building the UI

There is no building of the UI, just run the file in your browser or host it 
somewhere! It's a self-contained (sort of, it still uses external files, but no 
need to use a package manager) and can be run as-is, including locally as a file. 

I did it this way for simplicity and generalization. Feel free to extend as needed. 
