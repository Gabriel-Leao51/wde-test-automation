# language: en
Feature: OTP Login

  As a registered WDE Shop customer
  I want to log in using a one-time code emailed to me
  As an alternative to typing my password

  @auth @otp @happy-path
  Scenario: Customer logs in successfully using an emailed one-time code
    Given I am on the OTP login request page
    When I request a login code for "user2@example.com"
    Then I should be redirected to the OTP verification page
    When I retrieve the login code from Mailpit for "user2@example.com"
    And I submit the retrieved login code
    Then I should be logged in

  @auth @otp @security @happy-path
  Scenario: A login code becomes invalid after too many wrong attempts
    Given I am on the OTP login request page
    When I request a login code for "user2@example.com"
    And I submit an incorrect login code 5 times
    Then I should still be on the OTP verification page
    When I retrieve the login code from Mailpit for "user2@example.com"
    And I submit the retrieved login code
    Then I should still be on the OTP verification page
