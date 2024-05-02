rm -rf lib
pip install -r requirements.txt --platform manylinux2014_x86_64 --target lib --only-binary=:all:
(cd lib; zip ../lambda_function.zip -r .)
zip lambda_function.zip -u main.py
zip lambda_function.zip -u secrets.json