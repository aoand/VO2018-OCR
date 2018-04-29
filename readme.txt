0) create spool directory:

mkdir img-421135543

1) convert pdf to set of images page-xxx.png
pdftoppm img-421135543.pdf img-421135543/page -png

2) run OCR:

find img-421135543 -type f | sort | ./stand_alone.py > result.txt 2>errors.txt

DEBUG:

0) make sure that output debug directory exists:

mkdir -p test

1) run with one image:

./stand_alone.py --debug image.png

see analyzed squares in test/.
