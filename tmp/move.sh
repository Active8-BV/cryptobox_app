mkdir tmp
mv * tmp
cp ~/workspace/documentation/moved_to_uzziel .
cp ~/workspace/documentation/new_url.txt .
rm move.sh
git add *
git commit -am "final"
git push

