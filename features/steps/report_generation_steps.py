# features/steps/report_generation_steps.py
from behave import given, when, then
import os
import csv
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import the module to test
import generate_html_report

@given('a CSV file with printer page count data')
def step_csv_with_data(context):
    # Create a temporary CSV file with test data
    context.csv_file = os.path.join(context.temp_dir, 'test_printer_page_counts.csv')
    context.html_file = os.path.join(context.temp_dir, 'test_printer_report.html')
    
    # Create test data
    today = datetime.now().strftime("%Y-%m-%d")
    with open(context.csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([today, 5000, 100])
    
    # Mock the CSV_FILE and HTML_FILE paths
    with patch('generate_html_report.CSV_FILE', context.csv_file), \
         patch('generate_html_report.HTML_FILE', context.html_file):
        context.csv_patch = patch('generate_html_report.CSV_FILE', context.csv_file)
        context.html_patch = patch('generate_html_report.HTML_FILE', context.html_file)
        context.csv_patch.start()
        context.html_patch.start()

@given('the CSV file does not exist')
def step_csv_not_exist(context):
    # Set a non-existent CSV file path
    context.csv_file = os.path.join(context.temp_dir, 'non_existent_file.csv')
    context.html_file = os.path.join(context.temp_dir, 'test_printer_report.html')
    
    # Ensure the file doesn't exist
    if os.path.exists(context.csv_file):
        os.remove(context.csv_file)
    
    # Mock the CSV_FILE and HTML_FILE paths
    with patch('generate_html_report.CSV_FILE', context.csv_file), \
         patch('generate_html_report.HTML_FILE', context.html_file):
        context.csv_patch = patch('generate_html_report.CSV_FILE', context.csv_file)
        context.html_patch = patch('generate_html_report.HTML_FILE', context.html_file)
        context.csv_patch.start()
        context.html_patch.start()

@given('a CSV file with printer page count data for multiple days')
def step_csv_with_multiple_days(context):
    # Create a temporary CSV file with test data for multiple days
    context.csv_file = os.path.join(context.temp_dir, 'test_printer_page_counts.csv')
    context.html_file = os.path.join(context.temp_dir, 'test_printer_report.html')
    
    # Create test data for multiple days
    today = datetime.now()
    with open(context.csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Add data for the last 30 days
        for i in range(30, 0, -1):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            page_count = 5000 + (30 - i) * 100
            daily_increase = 100
            writer.writerow([date, page_count, daily_increase])
    
    # Mock the CSV_FILE and HTML_FILE paths
    with patch('generate_html_report.CSV_FILE', context.csv_file), \
         patch('generate_html_report.HTML_FILE', context.html_file):
        context.csv_patch = patch('generate_html_report.CSV_FILE', context.csv_file)
        context.html_patch = patch('generate_html_report.HTML_FILE', context.html_file)
        context.csv_patch.start()
        context.html_patch.start()

@when('I generate an HTML report')
def step_generate_html_report(context):
    # Generate the HTML report
    with patch('generate_html_report.CSV_FILE', context.csv_file), \
         patch('generate_html_report.HTML_FILE', context.html_file):
        # Call the main function to generate the report
        data = generate_html_report.read_csv_data()
        if data:
            html = generate_html_report.generate_html_table(data)
            generate_html_report.write_html_file(html)

@then('the HTML report should be created successfully')
def step_html_report_created(context):
    # Check if the HTML report was created
    assert os.path.exists(context.html_file), "HTML report was not created"
    
    # Check if the file has content
    with open(context.html_file, 'r') as htmlfile:
        content = htmlfile.read()
        assert len(content) > 0, "HTML report is empty"

@then('the report should contain the correct data')
def step_report_contains_data(context):
    # Check if the HTML report contains the expected data
    with open(context.html_file, 'r') as htmlfile:
        content = htmlfile.read()
        # Check for table data
        with open(context.csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                date, page_count, _ = row
                assert date in content, f"Date {date} not found in HTML report"
                assert page_count in content, f"Page count {page_count} not found in HTML report"

@then('the system should handle the error gracefully')
def step_handle_error_gracefully(context):
    # Check if the system handled the error without crashing
    try:
        with patch('generate_html_report.CSV_FILE', context.csv_file), \
             patch('generate_html_report.HTML_FILE', context.html_file):
            data = generate_html_report.read_csv_data()
            assert data is None, "Expected None when CSV file doesn't exist"
    except Exception as e:
        assert False, f"System did not handle error gracefully: {e}"

@then('the report should include daily usage data')
def step_report_includes_daily_data(context):
    # Check if the HTML report includes daily usage data
    with open(context.html_file, 'r') as htmlfile:
        content = htmlfile.read()
        assert "Daily Usage" in content or "daily" in content.lower(), "Daily usage data not found in report"

@then('the report should include monthly usage data')
def step_report_includes_monthly_data(context):
    # Check if the HTML report includes monthly usage data
    with open(context.html_file, 'r') as htmlfile:
        content = htmlfile.read()
        assert "Monthly Usage" in content or "monthly" in content.lower(), "Monthly usage data not found in report"

# Cleanup after each scenario
def after_scenario(context, scenario):
    # Stop any active patches
    if hasattr(context, 'csv_patch'):
        context.csv_patch.stop()
    if hasattr(context, 'html_patch'):
        context.html_patch.stop()
    
    # Remove temporary files
    if hasattr(context, 'csv_file') and os.path.exists(context.csv_file):
        os.remove(context.csv_file)
    if hasattr(context, 'html_file') and os.path.exists(context.html_file):
        os.remove(context.html_file)