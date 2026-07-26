# Scheduling MVP runtime logs

START_SCHEDULING_APP.bat writes Streamlit runtime logs and its temporary process-control files into this directory.

Generated log, JSON, temporary, and stop-request files are local runtime state and are excluded from Git. They can be inspected when diagnosing startup failures. Do not edit the process-control files while the launcher is running.
