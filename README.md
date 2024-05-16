# Requirements: 
- SQL
- django packages: mysqlclient, djangorestframework, django-cors-headers, Pillow, unidecode

# Setup SQL environment
https://www.youtube.com/watch?v=i0Ny3caKsrE&list=PLbiEmmDApLby83031AFtpTw2WUS9tvlEB&index=3
5:53-6:30

# kết nối vs CSDL: SQL
```console
python manage.py makemigrations
python manage.py migrate
```

# chạy server
```console
pip install --user virtualenv (nếu chưa có virtualenv)
python -m virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```
