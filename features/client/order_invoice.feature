# language: en
Feature: Customer Order Invoice Download

  As a registered WDE Shop customer
  I want to download a PDF invoice for my past orders
  To keep records of my purchases

  Background: Customer is logged in
    Given I am logged in as "customer"

  @order @invoice @happy-path
  Scenario: Customer downloads a PDF invoice for one of their orders
    When I navigate to the "Orders" page
    Then I should see a "Download Invoice" link for my order
    When I click the "Download Invoice" link
    Then a PDF file should be downloaded

  @order @invoice @security @happy-path
  Scenario: Requesting a non-existent order id returns 404 instead of a server error
    When I request the invoice for order id "000000000000000000000099"
    Then I should receive a 404 response
