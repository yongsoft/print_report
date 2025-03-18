import csv
import yaml  # Change from json to yaml
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Get the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct absolute path to config file
config_path = os.path.join(script_dir, 'config.yaml')  # Change from config.json to config.yaml

# Load configuration
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)  # Change from json.load to yaml.safe_load

# Configure logging
if config['logging']['enabled']:
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(script_dir, config['logging']['directory'])
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure the logger
    logger = logging.getLogger('report_logger')
    logger.setLevel(getattr(logging, config['logging']['level']))
    
    # Create a timed rotating file handler
    log_file = os.path.join(log_dir, 'report.log')
    handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=config['logging']['max_days']
    )
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# Construct absolute paths for all files
CSV_FILE = os.path.join(script_dir, config['csv_file_name'])
HTML_FILE = os.path.join(script_dir, config['report']['output_dir'], config['report']['output_file'])
TEMPLATE_FILE = os.path.join(script_dir, config['report']['template'])

def read_csv_data():
    """Reads data from the CSV file and returns a list of dictionaries."""
    data = {}
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip the header row
            for row in reader:
                date, total_page_count, net_increase = row
                date = str(date)  # Ensure date is treated as a string
                net_increase = int(net_increase)
                if date in data:
                    data[date]['net_increase'] += net_increase
                    data[date]['total_page_count'] = int(total_page_count)  # Keep the latest total_page_count
                else:
                    data[date] = {
                        'date': date,
                        'total_page_count': int(total_page_count),
                        'net_increase': net_increase
                    }
    except FileNotFoundError:
        error_msg = f"Error: CSV file '{CSV_FILE}' not found."
        logger.error(error_msg)
        print(error_msg)
        return None
    
    # Convert the dictionary to a list of dictionaries
    return list(data.values())

def generate_html_table(data):
    """Generates an HTML table with a bar chart and data switching from the given data."""
    if not data:
        return "<p>No data available.</p>"

    try:
        with open(TEMPLATE_FILE, 'r') as template_file:
            template = template_file.read()

        # Generate table rows
        table_rows = ''
        for item in data:
            table_rows += f"""
                <tr>
                    <td>{item['date']}</td>
                    <td>{item['net_increase']}</td>
                    <td>{item['total_page_count']}</td>
                </tr>
            """

        # Replace placeholders in the template
        # Replace placeholders with actual data
        html = template.replace('{table_rows}', table_rows)
        # Convert data to JSON string for JavaScript
        import json
        html = html.replace('{chart_data}', json.dumps(data))
        return html

    except FileNotFoundError:
        error_msg = f"Error: Template file '{TEMPLATE_FILE}' not found."
        logger.error(error_msg)
        print(error_msg)
        return "<p>Error: Template file not found.</p>"

def write_html_file(html):
    """Writes the HTML content to a file."""
    try:
        with open(HTML_FILE, 'w') as htmlfile:
            htmlfile.write(html)
        success_msg = f"HTML report generated successfully at '{HTML_FILE}'"
        logger.info(success_msg)
        print(success_msg)
    except Exception as e:
        error_msg = f"Error writing HTML file: {e}"
        logger.error(error_msg)
        print(error_msg)

if __name__ == "__main__":
    data = read_csv_data()
    if data:
        html = generate_html_table(data)
        write_html_file(html)