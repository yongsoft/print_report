Feature: Printer Page Count
  As a system administrator
  I want to retrieve the printer's page count
  So that I can track printer usage

  Scenario: Successfully retrieve page count
    Given a printer with IP address 192.168.1.100
    When I query the printer for its page count
    Then I should receive a valid page count
    And the page count should be stored in the CSV file

  Scenario: Calculate page count increase
    Given a printer with IP address 192.168.1.100
    And a printer with previous page count of 4500
    When I query the printer and receive a page count of 4600
    Then the page count should be stored in the CSV file
    And the net increase should be 100 pages