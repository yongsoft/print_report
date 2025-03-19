# features/steps/connectivity_steps.py
from behave import given, when, then
import asyncio
import os
from unittest.mock import patch, MagicMock

# Import the module to test
import printer

@given('a printer with IP address {ip_address}')
def step_printer_with_ip(context, ip_address):
    # Store the IP address in the context
    context.ip_address = ip_address
    # Create a temporary directory for test files
    import tempfile
    context.temp_dir = tempfile.mkdtemp()

@when('I check the printer connectivity')
def step_check_connectivity(context):
    # Mock the SNMP response for connectivity check
    with patch('printer.getCmd') as mock_get_cmd:
        # Configure the mock to return a successful response
        mock_var_bind = MagicMock()
        mock_var_bind.__getitem__.side_effect = lambda i: mock_var_bind if i == 0 else "Printer Description"
        mock_get_cmd.return_value = (None, 0, 0, [mock_var_bind])
        
        # Run the connectivity check function
        context.connectivity_result = asyncio.run(printer.check_network_connectivity(context.ip_address, 'public'))

@when('the printer is offline')
def step_printer_offline(context):
    # Mock the SNMP response for a failed connectivity check
    with patch('printer.getCmd') as mock_get_cmd:
        # Configure the mock to return an error
        mock_get_cmd.return_value = ("Timeout", None, None, None)
        
        # Run the connectivity check function
        context.connectivity_result = asyncio.run(printer.check_network_connectivity(context.ip_address, 'public'))

@then('the connectivity check should succeed')
def step_connectivity_check_success(context):
    # Check if the connectivity check was successful
    assert context.connectivity_result is True, "Connectivity check failed"

@then('the connectivity check should fail')
def step_connectivity_check_fail(context):
    # Check if the connectivity check failed
    assert context.connectivity_result is False, "Connectivity check succeeded when it should have failed"

@then('the system should use the previous page count')
def step_use_previous_count(context):
    # Check if the system used the previous page count
    with patch('printer.read_previous_page_count', return_value=(context.previous_count, None)), \
         patch('printer.write_page_count') as mock_write:
        # Run the page count query function with a failed connectivity check
        with patch('printer.check_network_connectivity', return_value=False):
            asyncio.run(printer.get_printer_page_count(context.ip_address, 'public'))
        
        # Check if write_page_count was called with the previous count
        mock_write.assert_called_once()
        args, _ = mock_write.call_args
        assert args[1] == context.previous_count, f"Expected {context.previous_count}, got {args[1]}"