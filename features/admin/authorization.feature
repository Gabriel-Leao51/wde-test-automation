# language: en
Feature: Security - Admin Panel Authorization
  As a logged-in customer user (without admin permissions)
  I must not be able to access admin panel pages or functionality
  To ensure only administrators can manage the store

  Background: Logged-in customer user
    Given I am logged in as "customer"

  # KNOWN BUG (BUG-AUTH-001): This scenario MUST FAIL if the bug persists
  @xfail
  Scenario: Attempt to directly access Admin Products as a customer user
    When I try to access the URL "/admin/products"
    Then I should NOT be able to access the Admin Products page

  # KNOWN BUG (BUG-AUTH-002): This scenario MUST FAIL if the bug persists
  @xfail
  Scenario: Attempt to directly access Admin Orders as a customer user
    When I try to access the URL "/admin/orders"
    Then I should see a message indicating lack of authorization

  # KNOWN BUG (BUG-AUTH-001): This scenario MUST FAIL if the bug persists
  @xfail
  Scenario: Attempt to directly access the Edit Product form as a customer user
    When I try to access the URL "/admin/products/000000000000000000000001"
    Then I should NOT be able to access the Edit Product form
