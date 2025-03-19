Feature: Report Generation
  As a system administrator
  I want to generate HTML reports from printer data
  So that I can visualize printer usage

  Scenario: Generate HTML report from CSV data
    Given a CSV file with printer page count data
    When I generate an HTML report
    Then the HTML report should be created successfully
    And the report should contain the correct data

  Scenario: Handle missing CSV file
    Given the CSV file does not exist
    When I generate an HTML report
    Then the system should handle the error gracefully

  Scenario: Generate report with daily and monthly views
    Given a CSV file with printer page count data for multiple days
    When I generate an HTML report
    Then the report should include daily usage data
    And the report should include monthly usage data