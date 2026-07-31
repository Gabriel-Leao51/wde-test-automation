# language: en
@toast
Feature: Toast Notifications
  As a shopper
  I want transient confirmation feedback after actions
  So that I know an action succeeded without a disruptive native alert

  Background: Customer is logged in
    Given I am logged in as "customer"

  Scenario: Adding a product to the cart shows a success toast that disappears on its own
    When I click "View Details" for the product "GTRACING - Black Gaming Chair"
    And I click the "Add to Cart" button on the product details page
    Then I should see a success toast saying "Added to cart!"
    And the toast should disappear on its own
