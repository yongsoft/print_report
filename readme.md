# Printer Usage Report

A Python-based utility for monitoring printer page counts via SNMP, tracking usage over time, and generating HTML reports.

Curently We have tested the application with HP Smart Tank 51x Series. 
An example of generated report can be find : reports/printer_report.html

## Features

- Automated printer page count collection via SNMP
- Daily tracking of printer usage
- Automatic filling of missing dates in data
- HTML report generation with usage statistics
- Configurable logging and reporting options
- YAML-based configuration

## Requirements

- Python 3.6+
- PySNMP
- PyYAML

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd print_report
```

2. Install dependencies:
```bash
pip install pysnmp pyyaml
```

3. Configure your printer settings in `config.yaml`

## Configuration

Edit the `config.yaml` file to match your environment:

```yaml
printer:
  ip_address: "192.168.1.100"  # Replace with your printer's IP
  port: 161
  community_string: "public"
  timeout: 2

logging:
  enabled: true
  directory: "logs"
  level: "INFO"
  max_days: 30

csv_file_name: "printer_page_counts.csv"

report:
  output_dir: "reports"
  format: "html"
  template: "templates/report_template.html"
  output_file: "printer_report.html"
```

## Usage

### Collecting Printer Data

Run the data collection script:

```bash
python printer.py
```

This will:
- Connect to the printer using SNMP
- Retrieve the current page count
- Record the data in a CSV file
- Fill in any missing dates in the data

### Generating Reports

Generate an HTML report of printer usage:

```bash
python generate_html_report.py
```

The report will be saved in the configured output directory.

## Directory Structure

```
print_report/
├── config.yaml           # Configuration file
├── printer.py            # Main data collection script
├── generate_html_report.py  # Report generation script
├── templates/            # HTML templates
│   └── report_template.html
├── reports/              # Generated reports
├── logs/                 # Log files
└── printer_page_counts.csv  # Collected data
```

## Scheduling

For automated data collection, consider setting up a cron job (Linux/Mac) or Task Scheduler (Windows) to run the script daily.

Example cron entry (runs daily at 11:59 PM):
```
59 23 * * * cd /path/to/print_report && python printer.py
```

## License

MIT License. 