#!/bin/bash

# Exectue Amelia Pipeline with RPD tracer active
echo "Running RPD tracer on main.py"
bash ./rocmProfileData/rpd_tracer/runTracer.sh python main.py

echo "Trace complete. Output: $(pwd)/trace.rpd"

# JSON conversion if specified
if [ "$1" = "-json" ]; then
    echo "Converting trace.rpd to json..."
    python ./rocmProfileData/tools/rpd2tracing.py trace.rpd trace.json
    echo "Conversion finished. Output $(pwd)/trace.json"
fi

exit 0