# language: en
Feature: Customer E2E Purchase Flow

  As a registered WDE Shop customer
  I want to find a specific product, add it to the cart,
  and complete the purchase using test payment
  To ensure the main acquisition process works correctly

  Background: Customer is logged in
    Given I am logged in as "customer"

  Scenario: Customer successfully purchases a specific product
    When I click "View Details" for the product "GTRACING - Black Gaming Chair"
    And I click the "Add to Cart" button on the product details page
    Then the cart indicator in the navigation bar should be updated to "1"
    When I click the "Cart" link in the navigation bar
    Then I should see the product "GTRACING - Black Gaming Chair" listed in the cart
    When I click the "Buy Products" button
    Then I should be redirected to the external Stripe payment page
    When I fill in the Stripe test card details and confirm payment
    Then I should be redirected to the order success page
    And I should receive an order confirmation email in Mailpit
