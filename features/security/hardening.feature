# language: en
Feature: Advanced Security - Application Hardening

  As an application that processes user and payment data
  I must protect against common attack techniques and avoid leaking internal details
  To ensure the system's integrity, availability, and confidentiality

  @security @injection @happy-path
  Scenario: NoSQL injection attempt on login does not crash the app or bypass authentication
    When I send a NoSQL injection payload to "/login"
    Then I should receive an invalid credentials response
    And the application should remain up

  @security @injection @happy-path
  Scenario: NoSQL injection attempt on signup does not crash the app
    When I send a NoSQL injection payload to "/signup"
    Then the application should remain up

  # KNOWN BUG (BUG-SEC-002): missing security headers
  @security @headers @xfail
  Scenario: The application should respond with standard security headers
    When I make a GET request to "/products"
    Then the response should contain the header "x-content-type-options" with value "nosniff"
    And the response should contain the header "x-frame-options"
    And the response should contain the header "content-security-policy"
    And the response should not contain the header "x-powered-by"

  # KNOWN BUG (BUG-SEC-003): CSRF token exposed in the form URL
  @security @csrf @xfail
  Scenario: The CSRF token should not be exposed in the product form URL
    Given I am logged in as "admin"
    When I visit the new product page
    Then the form's action attribute should not contain "_csrf"

  # KNOWN BUG (BUG-SEC-004): session cookie missing Secure/SameSite flags
  @security @session @xfail
  Scenario: The session cookie should have the Secure and SameSite flags configured
    When I make a GET request to "/login"
    Then the session cookie should have the Secure flag enabled
    And the session cookie should have the SameSite flag configured

  # KNOWN BUG (BUG-INFO-001): error messages expose internal server details
  @security @error-handling @xfail
  Scenario: Internal errors should not expose server file paths and source code
    When I send a request that triggers an internal server error
    Then the response should not contain server filesystem paths
    And the response should not contain server source code snippets

  # KNOWN BUG (BUG-SEC-005): hardcoded session secret allows forging valid cookies
  @security @session @xfail
  Scenario: A session cookie forged with the hardcoded secret should not grant access
    When I forge an admin session cookie using the hardcoded secret from the source code
    And I access "/admin/products" using only the forged cookie
    Then access should NOT be granted without a real login
