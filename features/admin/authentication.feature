# language: en
Feature: Security - Admin Panel Authentication
  As an unauthenticated visitor
  I must not be able to access protected admin panel pages
  To ensure system security

  Scenario: Attempt to directly access Admin Products without being logged in
    When I try to access the URL "/admin/products" without being logged in
    Then I should be redirected to the 401 error page
    And I should see the unauthenticated page elements

  Scenario: Attempt to directly access Admin Orders without being logged in
    When I try to access the URL "/admin/orders" without being logged in
    Then I should be redirected to the 401 error page
    And I should see the unauthenticated page elements
