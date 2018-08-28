yapf -i -r .
yes | isort -rc > /dev/null
js-beautify -r $(find templates/ -type f -follow -print)
