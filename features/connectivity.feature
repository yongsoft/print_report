Feature: Printer Connectivity
  As a system administrator
  I want to check if the printer is reachable via SNMP
  So that I can ensure the monitoring system works correctly

  Scenario: Successfully connect to a printer
    Given a printer with IP address 192.168.1.100
    When I check the printer connectivity
    Then the connectivity check should succeed

  Scenario: Handle offline printer
    Given a printer with IP address 192.168.1.100
    When the printer is offline
    Then the connectivity check should fail

  Scenario: Use previous page count when printer is offline
    Given a printer with IP address 192.168.1.100
    And a printer with previous page count of 4500
    When the printer is offline
    Then the system should use the previous page count