rm -rf /tmp/covid19*
python3 src/covid19/lk_vax_centers.py

git reset --hard HEAD
git checkout data
git pull origin data
git clean -f -d
cp /tmp/covid19* ./
git add .
git commit -m "Added local_workflows/download-lk-vax-center.sh output"
git push origin data
git checkout main
