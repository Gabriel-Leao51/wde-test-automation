# language: en
@visual
Feature: Visual Regression - Key application pages
  As someone responsible for WDE Shop quality
  I want to compare screenshots of key pages against an approved baseline
  To detect unintended visual layout/CSS changes

  Scenario: Login page
    When I visit the login page
    Then the page should match the "login_page" snapshot

  Scenario: Product catalog
    When I visit the product catalog
    Then the page should match the "products_catalog" snapshot

  Scenario: Product details page
    When I visit the product details page "000000000000000000000001"
    Then the page should match the "product_details" snapshot

  Scenario: Admin product management panel
    Given I am logged in as "admin"
    When I visit the manage products panel
    Then the page should match the "admin_manage_products" snapshot

  Scenario: 401 error page
    When I try to access a protected page without being logged in
    Then the page should match the "error_401" snapshot
