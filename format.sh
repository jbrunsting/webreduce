yapf -i -r .
yes | isort -rc > /dev/null
js-beautify -n -r $(find templates/ -type f -follow -print)
sass-convert -i $(find . -name "*.scss")
