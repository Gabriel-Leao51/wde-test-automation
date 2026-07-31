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
