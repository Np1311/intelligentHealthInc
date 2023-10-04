echo "BUILD START"
export CACHE_VERSION=$(($CACHE_VERSION + 1))

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --cache-dir=$CACHE_DIR -r requirements.txt
python manage.py collectstatic --noinput
echo "BUILD END"