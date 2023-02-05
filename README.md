# JWT Authentication & Authorization Example

This simple web app was written for the _Authentication & Authorization using JSON Web Tokens_ 
presentation purposes which was shown during the 
[wroc.py meetup event](https://www.meetup.com/wrocpy/events/288952995/).

### Installation in the isolated environment using [venv](https://docs.python.org/3/library/venv.html)
1. Go to the jwt-auth's main directory, i.e. to the directory where this `README.md` file is located.
1. Create a virtual environment (jwt-auth requires `python 3.11` installed)
    ```sh
    python3.11 -m venv ./venv/
    ```
1. Activate new virtual environment
    ```sh
    source ./venv/bin/activate
    ```
1. Install requirements
    ```sh
    pip install poetry && poetry install
    ```
1. To exit, simply type
    ```sh
    deactivate
    ```
