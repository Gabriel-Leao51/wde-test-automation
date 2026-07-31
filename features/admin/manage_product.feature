# language: en
Feature: Manage Products - Admin Panel

    As a logged-in administrator
    I want to be able to manage products in the admin panel
    To keep the store's catalog up to date

    Background:
        Given I am logged in as "admin"
        And I am on the admin panel home page "/products"
        When I navigate to the manage products page "Manage Products"

    @crud @product @happy-path @xdist_group_product_crud
    Scenario: Successfully add a new product
        When I click the "Add Product" button
        And I fill in the add product form with the following data:
            | Field       | Value                                    |
            | title       | Test Mousepad                            |
            | image       | mousepad.jpg                             |
            | summary     | A great mousepad for testing             |
            | price       | 35                                       |
            | department  | Office                                   |
            | description | Ideal mousepad for automated testing     |
        And I click the "Save" button
        Then I should be redirected to the manage products page "/admin/products"
        And the product "Test Mousepad" should be visible in the product list with title and image

    @crud @product @happy-path @xdist_group_product_crud
    Scenario: Successfully edit an existing product
        When I click the "View & Edit" button for the product titled "Test Mousepad"
        And I fill in the edit product form with the following data:
            | Field       | Value                                          |
            | title       | Edited Test Mousepad                           |
            | summary     | Edited Test Mousepad Summary                   |
            | price       | 40                                             |
            | description | Edited description of the ideal test mousepad |
        And I click the "Save" button
        Then I should be redirected to the manage products page "/admin/products"
        And the product "Edited Test Mousepad" should be displayed in the product list with the updated title

    @crud @product @happy-path @xdist_group_product_crud
    Scenario: Cancelling the delete confirmation keeps the product
        When I click the "Delete" button for the product titled "Edited Test Mousepad"
        Then I should see a confirmation dialog to delete "Edited Test Mousepad"
        When I cancel the deletion
        Then the product "Edited Test Mousepad" should still be displayed in the product list

    @crud @product @happy-path @xdist_group_product_crud
    Scenario: Successfully delete an existing product
        When I click the "Delete" button for the product titled "Edited Test Mousepad"
        Then I should see a confirmation dialog to delete "Edited Test Mousepad"
        When I confirm the deletion
        Then the product "Edited Test Mousepad" should no longer be displayed in the product list

    @validation @product @negative-path
    Scenario: Add a product with the required name field blank
        When I click the "Add Product" button
        And I fill in the add product form with the following data:
            | Field       | Value                                 |
            | image       | mousepad.jpg                          |
            | summary     | A great mousepad for testing          |
            | price       | 35                                    |
            | description | Ideal mousepad for automated testing  |
        And I click the "Save" button
        Then I should see an error message stating that required fields must be filled in
        And I should remain on the add product page
