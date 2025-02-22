# filename without .md extension
filename=$(basename -- "$1" .md)
path=$(dirname -- "$1")
title=$(head -n 1 "$1")
pandoc -f markdown+smart -t epub3 -o output/$filename.epub --css style.css --resource-path "$path" --metadata title="$title" $1