GOOGLE_DRIVE_API_KEY=$1
python3 src/covid19/lk_vax_centers/lk_vax_centers_pipe.py --google_drive_api_key $GOOGLE_DRIVE_API_KEY

git add .
git commit -c "Pre Data Load"

git checkout data
git pull origin data
git clean -f -d
cp /tmp/covid19* ./
git add .
git commit -m "Added local_workflows/download-lk-vax-center.sh output"
git push origin data
git checkout main
open https://github.com/nuuuwan/covid19/tree/data
