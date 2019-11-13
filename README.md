# ES-Composer
Composer Web App for Service Engineering for University of Aveiro


To Run Windows:

    python -m venv venv
    venv\Scripts\activate

    pip install -r requirements.txt

    flask run --port 8000 --cert=cert.crt --key=cert.key

To Run Linux:

    python -m venv venv
    source venv/bin/activate

    pip install -r requirements.txt

    flask run --port 8000 --cert=cert.crt --key=cert.key
