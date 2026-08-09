# language: en
@localization
Feature: Language Selector
  As a shopper
  I want to switch the storefront language
  So that I can browse the store in my preferred language

  Scenario Outline: Switching the language via the nav selector updates visible text
    Given I am on the product catalog
    When I select "<language_code>" from the language dropdown
    Then the navigation should show "<shop_label>" as the shop link
    And the product catalog heading should read "<catalog_heading>"

    Examples:
      | language_code | shop_label | catalog_heading    |
      | EN             | Shop       | All Products       |
      | PT             | Loja       | Todos os Produtos  |

  Scenario: Product catalog content is localized, not just navigation chrome
    Given the language is set to "pt"
    When I view the product with id "000000000000000000000001"
    Then I should see the product titled "GTRACING - Cadeira Gamer Preta"
