rm -rf /tmp/covid19*
git reset --hard HEAD
git branch data
python3 src/covid19/lk_vax_centers.py
cp /tmp/covid19* ./
git add .
git commit -m "Added local_workflows/download-lk-vax-center.sh output"
git push origin data
git branch master
