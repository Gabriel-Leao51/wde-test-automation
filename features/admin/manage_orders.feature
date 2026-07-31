# language: en
Feature: Manage Orders - Admin Panel

    As a logged-in administrator
    I want to be able to manage order status in the admin panel
    To keep the store's sales records up to date

    Background:
        Given I am logged in as "admin"
        And I navigate to the manage orders page

    @crud @order @happy-path
    Scenario: Successfully change an order's status to "Fulfilled"
        Given a known order with status "Pending" exists
        When I locate the known order in the order list
        And I select the new status "Fulfilled" for this order
        And I click the "Update" button for this order
        Then the status "FULFILLED" should be displayed for this order
        And I should see a success toast saying "Order status updated!"
