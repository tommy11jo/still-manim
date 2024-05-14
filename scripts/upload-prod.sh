#!/bin/bash
echo "Uploading the package to PyPi..."
twine upload --repository pypi dist/*