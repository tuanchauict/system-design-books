# Simplified input
input=$1

# Find the matching file
matches=($(find . -type f -name "$input*.md"))

# Check if there are no matches or multiple matches
if [ ${#matches[@]} -eq 0 ]; then
    echo "Error: No matching files found for pattern '$input*.md'"
    exit 1
elif [ ${#matches[@]} -gt 1 ]; then
    echo "Error: Multiple matching files found for pattern '$input*.md'"
    exit 1
fi
# Use the single matching file
file=${matches[0]}
# filename without .md extension
filename=$(basename -- "$file" .md)
path=$(dirname -- "$file")
title=$(sed -n '2p' "$file")

echo $filename
echo $title 

pandoc -f markdown+smart -t epub3 \
    -o output/$filename.epub \
    --css style.css \
    --resource-path "$path" \
    --metadata title="$title" \
    --highlight-style pygments \
    $file
