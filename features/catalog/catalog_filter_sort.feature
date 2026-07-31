# language: en
@catalog
Feature: Product Catalog - Filtering and Sorting
  As a shopper
  I want to filter and sort the product catalog
  So that I can find what I'm looking for more easily

  Scenario: Filtering the catalog by department
    When I visit the product catalog filtered by department "Sports"
    Then only products from the "Sports" department should be listed

  Scenario Outline: Sorting the catalog by name
    When I visit the product catalog sorted by "<sort>"
    Then the listed products should be in <order> alphabetical order

    Examples:
      | sort      | order      |
      | name_asc  | ascending  |
      | name_desc | descending |

  Scenario Outline: Sorting the catalog by price
    When I visit the product catalog sorted by "<sort>"
    Then the listed products should be in <order> price order

    Examples:
      | sort       | order      |
      | price_asc  | ascending  |
      | price_desc | descending |

  Scenario: An unrecognized sort value is ignored rather than breaking the page
    When I visit the product catalog sorted by "not_a_real_sort"
    Then the product catalog page should load successfully

  Scenario: Filtering the catalog via the department dropdown
    Given I am on the product catalog
    When I select "Sports" from the department filter
    And I click the "Filter" button
    Then only products from the "Sports" department should be listed

  Scenario: Sorting the catalog via the sort dropdown
    Given I am on the product catalog
    When I select "Price: Low to High" from the sort dropdown
    And I click the "Filter" button
    Then the listed products should be in ascending price order

  Scenario: Live search suggests matching products as I type
    Given I am on the product catalog
    When I type "chair" into the product search box
    Then I should see search suggestions including "GTRACING - Black Gaming Chair"
    And I should see search suggestions including "Ergonomic Office Chair"

  Scenario: Selecting a live search suggestion navigates to that product
    Given I am on the product catalog
    When I type "chair" into the product search box
    And I click the search suggestion "Ergonomic Office Chair"
    Then I should see the product titled "Ergonomic Office Chair"

  Scenario: The search API returns matching products as JSON
    When I request the search API with query "yoga"
    Then the JSON response should include a product titled "Yoga Mat"
