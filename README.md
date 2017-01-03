# Web UI for Robinhood

This project aims to be an alternative, or supplamental, web interface for 
the popular Robinhood Financial trading application. It uses unpublished 
Robinhood APIs so use with caution.

The UI can be hosted locally for security reasons and supports both 
username & password authentication as well as direct token authentication. There 
is also no database in use here and local browser storage is used for persistence. 


## Getting Started
### Building the API service

**Prerequisites**

* [Python 2.x](https://www.python.org/downloads/)

**Install guide**

Change directories into the */api/* project folder. Then simply 
install the project requirements by running `pip install -r requirements`

This will install Flask(-RESTful) which is what the project uses to create 
the API service. That's all of the requirements needed. 

To run the service, execute ```python api.py```

You should now have an API service running on default port 5000. 

### Building the UI

There is no building of the UI, just run the */ui/index.html* file in your browser or host it 
somewhere! It's a self-contained (sort of, it still uses external files, but no 
need to use a package manager) and can be run as-is, including locally as a file. 

I did it this way for simplicity and generalization. Feel free to extend as needed. 


## Additional Information
### Getting a Robinhood API access token

The following snippet will get you an API access token for use with the 
Robinhood API (and, inherently, this project's API as an alternate form 
of authentication). Replace the *YOUR_\** values with your actual 
username and password for Robinhood. 

```bash
curl -X 'POST' \
	-H 'Accept: application/json' \
	-d 'username=YOUR_USERNAME&password=YOUR_PASSWORD' \
	'https://api.robinhood.com/api-token-auth/'
```

### Test your API access token

The easiest way to test your access token is to just attempt to use it to get your 
account information using the following command. Replace *YOUR_API_TOKEN* with your 
API token from the previous section.

```bash
curl -X 'GET' \
	-H 'Accept: application/json' \
    -H 'Authorization: Token YOUR_API_TOKEN' \
    'https://api.robinhood.com/user/' | python -m json.tool
```

