#!/bin/bash
echo "Uploading the package to PyPi..."
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*