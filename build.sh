pip install --upgrade pip

pip install -r requirements.txt

pip uninstall tensorflow
pip uninstall azure-storage-blob

python manage.py makemigrations 
python manage.py migrate