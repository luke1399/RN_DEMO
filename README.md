# Radio Networks Research Dashboard

Streamlit dashboard for exploring synthetic radio-network RSRP measurements.

## Features

- Interactive coverage map built with `pydeck`
- Signal-strength distribution plot built with `plotly`
- Sidebar filters for signal selection and minimum RSRP threshold
- Mock data generator for synthetic measurement samples with fading effects

## Project Structure

```text
.
├── app.py
├── data/
│   └── measurements.csv
├── requirements.txt
└── utils/
    └── generate_mock_data.py
```

## Requirements

- Python 3.10+

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Generate Mock Data

Generate the synthetic measurement dataset manually:

```bash
python utils/generate_mock_data.py
```

This creates `data/measurements.csv` with 200 samples and the following fields:

- `LATITUDE`
- `LONGITUDE`
- `RSRP_1`
- `RSRP_2`
- `RSRP_3`
- `RSRP_4`
- `RSRP_5`

Note: if `data/measurements.csv` does not exist, the app will generate it automatically on startup.

## Launch The App

Start the Streamlit dashboard with:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Typical Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python utils/generate_mock_data.py
streamlit run app.py
```
