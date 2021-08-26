git checkout main
git pull origin main

GOOGLE_API_KEY=$1
python3 src/covid19/lk_vax_centers/lk_vax_centers_pipe.py --google_api_key=$GOOGLE_API_KEY
