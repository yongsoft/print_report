# features/steps/page_count_steps.py
from behave import given, when, then
import asyncio
import os
import csv
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the module to test
import printer

@when('I query the printer for its page count')
def step_query_printer_page_count(context):
    # Mock the SNMP response for page count
    with patch('printer.getCmd') as mock_get_cmd:
        # Configure the mock to return a page count
        mock_var_bind = MagicMock()
        mock_var_bind.__getitem__.side_effect = lambda i: mock_var_bind if i == 0 else 5000
        mock_get_cmd.return_value = (None, 0, 0, [mock_var_bind])
        
        # Run the page count query function
        asyncio.run(printer.get_printer_page_count(context.ip_address, 'public'))

@given('a printer with previous page count of {count:d}')
def step_previous_page_count(context, count):
    # Create a CSV file with a previous page count
    context.previous_count = count
    context.csv_file = os.path.join(context.temp_dir, 'test_printer_page_counts.csv')
    
    # Write the previous count to the CSV file
    yesterday = (datetime.now() - printer.timedelta(days=1)).strftime("%Y-%m-%d")
    with open(context.csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([yesterday, count, 0])
    
    # Mock the read_previous_page_count function
    with patch('printer.read_previous_page_count') as mock_read:
        mock_read.return_value = (count, yesterday)
        context.mock_read = mock_read

@when('I query the printer and receive a page count of {count:d}')
def step_receive_page_count(context, count):
    # Mock the SNMP response for page count
    with patch('printer.getCmd') as mock_get_cmd, \
         patch('printer.CSV_FILE', context.csv_file), \
         patch('printer.read_previous_page_count', return_value=(context.previous_count, None)):
        
        # Configure the mock to return the specified page count
        mock_var_bind = MagicMock()
        mock_var_bind.__getitem__.side_effect = lambda i: mock_var_bind if i == 0 else count
        mock_get_cmd.return_value = (None, 0, 0, [mock_var_bind])
        
        # Run the page count query function
        asyncio.run(printer.get_printer_page_count(context.ip_address, 'public'))

@then('I should receive a valid page count')
def step_valid_page_count(context):
    # Check if the page count was retrieved and written to the CSV file
    with open(context.csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        assert len(rows) > 0, "No data was written to the CSV file"
        assert int(rows[-1][1]) > 0, "Page count should be greater than 0"

@then('the page count should be stored in the CSV file')
def step_page_count_stored(context):
    # Check if the page count was stored in the CSV file
    assert os.path.exists(context.csv_file), "CSV file was not created"
    with open(context.csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

@then('the net increase should be {increase:d} pages')
def step_net_increase(context, increase):
    # Check if the net increase was calculated correctly
    with open(context.csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        assert len(rows) > 0, "No data was written to the CSV file"
        assert int(rows[-1][2]) == increase, f"Expected net increase of {increase}, got {rows[-1][2]}"