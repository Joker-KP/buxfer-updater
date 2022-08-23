#!/bin/bash

# copy UI Vision RPA macros as exemplary files and remove any encrypted data from them

files=$(find uivision-data/macros/accounts -name "???????.json")
for file in $files; do
  echo "Processing file: $file"
  cp "$file" "$file.example"
  sed -i 's/__RPA_ENCRYPTED__[a-z0-9]*/__PLACEHOLDER__/g' "$file.example"
done
