# features/environment.py
import os
import tempfile
import shutil

def before_all(context):
    """Setup before all tests"""
    # Create a base temporary directory for all tests
    context.base_temp_dir = tempfile.mkdtemp()
    print(f"Created base temporary directory: {context.base_temp_dir}")

def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Create a temporary directory for this scenario
    context.temp_dir = tempfile.mkdtemp(dir=context.base_temp_dir)
    print(f"Created temporary directory for scenario: {context.temp_dir}")

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Clean up any patches that might be active
    if hasattr(context, 'csv_patch') and context.csv_patch:
        context.csv_patch.stop()
    if hasattr(context, 'html_patch') and context.html_patch:
        context.html_patch.stop()
    
    # Remove temporary files specific to this scenario
    if hasattr(context, 'temp_dir') and os.path.exists(context.temp_dir):
        try:
            shutil.rmtree(context.temp_dir)
            print(f"Removed temporary directory: {context.temp_dir}")
        except Exception as e:
            print(f"Failed to remove temporary directory: {e}")

def after_all(context):
    """Cleanup after all tests"""
    # Remove the base temporary directory
    if hasattr(context, 'base_temp_dir') and os.path.exists(context.base_temp_dir):
        try:
            shutil.rmtree(context.base_temp_dir)
            print(f"Removed base temporary directory: {context.base_temp_dir}")
        except Exception as e:
            print(f"Failed to remove base temporary directory: {e}")