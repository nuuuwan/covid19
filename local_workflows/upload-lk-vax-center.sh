git checkout main
git pull origin main

git checkout data
git pull origin data
git clean -f -d
cp /tmp/covid19* ./
git add .
git commit -m "Added local_workflows/download-lk-vax-center.sh output"
git push origin data

git checkout main
open https://github.com/nuuuwan/covid19/tree/data
