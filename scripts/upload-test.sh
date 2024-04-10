#!/bin/bash
echo "Uploading the package to TestPyPI..."
twine upload --repository testpypi dist/*