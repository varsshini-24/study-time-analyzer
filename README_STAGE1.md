# StudyFlow — Stage 1 Premium Dashboard Update

This package updates the existing StudyFlow project in place. It does not include your database, virtual environment, or Git metadata.

## Included files

- `app.py` — refreshed premium styling and interactive Plotly charts on Overview.
- `analysis.py` — database path now resolves relative to the project file, not the shell's current directory.
- `requirements.txt` — explicit Streamlit, Pandas, Plotly, and NumPy dependencies.
- `test_stage1.py` — synthetic-data smoke test for existing analysis helpers and Plotly.

## Apply safely on Windows

1. Close the running Streamlit app with `Ctrl+C`.
2. Open `E:\study-time-analyzer` in File Explorer. Make a backup copy of `app.py`, `analysis.py`, and `requirements.txt` before overwriting them.
3. Extract these files directly into `E:\study-time-analyzer` and choose **Replace** for the three existing files. Keep your existing `data\study.db`, `.git`, and `venv` folders.
4. Open PowerShell in `E:\study-time-analyzer` and run:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python test_stage1.py
python -m py_compile app.py analysis.py database.py
python -m streamlit run app.py
```

If PowerShell does not allow virtual-environment activation, you can run the project interpreter directly instead:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe test_stage1.py
.\venv\Scripts\python.exe -m py_compile app.py analysis.py database.py
.\venv\Scripts\python.exe -m streamlit run app.py
```

## Manual acceptance test

- Open Overview and confirm all four charts render without exceptions.
- Hover over chart marks and confirm tooltips display.
- Check that all existing sidebar pages still open.
- Add one test session and confirm it appears in Study History and Overview.
- Stop the app and restart it; confirm the session remains.
- Check that the project uses the existing `data\study.db` file.

## Scope

This is Stage 1 only. Consistency tracking, weekly goals, enhanced insights, and report exports should be added and tested in separate stages after the dashboard passes the acceptance test.
