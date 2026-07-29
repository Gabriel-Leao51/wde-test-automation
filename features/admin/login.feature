# language: en
Feature: Admin Login
    As an administrator
    I want to log in to the admin panel
    To access the system's management features

    @auth @login-admin @happy-path
    Scenario: Successful admin login
        Given I am on the admin login page
        When I enter a valid admin email
        And I enter a valid admin password
        And I click the "Login" button
        Then I should be redirected to the admin panel home page
        And I should see the "Manage Products" and "Manage Orders" menu options
        And I should see the "Logout" button in the header

    @auth @login-admin @negative-case
    Scenario: Admin login fails - Invalid credentials
        Given I am on the login page
        When I enter an invalid email
        And I enter an invalid password
        And I click the "Login" button
        Then I should see an error message
        And I should remain on the login page
