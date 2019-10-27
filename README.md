# CS9163 - Application Security

## Assignment 2 - Flask Web App for Spell Checker

Joel Castillo (JC5383)

### Assignment Description

This assignment focuses on secure Web development. For this assignment, you are tasked withturning your spell checking system from Assignment 1 into a Web service using Flask, while focusing on the security of the Web service you are implementing. After you develop the secure Web service, you will test it to ensure it is not vulnerable to common attacks. Though it is not part of the grade, you should continue to use the secure development practices that you established in Assignment 1.

- User registration: /your/webroot/register
- User login: /your/webroot/login
- Mock Two-factor authentication: /your/webroot/login
- Text submission: /your/webroot/spell_check
- Result retrieval: /your/webroot/spell_check

## Report Details

For this version of the application, the following dependencies are required:

- Flask - This is the web framework required for the assignment. Included in its dependencies are:
  - Werkzeug - A WSGI library written in Python (which Flask wraps) 
  - Jinja - A template engine with a sandboxed exxxecution environment for embedding python code within your HTML templates (or other templates)
- Flask-WTF - An extension for flask that integrates with WTForms, a Python Forms liibary. It also provides CSRF protection (more on this later). 

When implementing the project a few design decision were made:

- The data store for the application is a simple python dictionary. This means that the dictionary loses its data whenever the application is restarted. However, this means that this implementation did not have to implement protection for SQLi attachs against a relational database
- There is a limited amount of HTML code. No javascript is used for the application. This limits the attack surface by reducing the number of third party imports and also improves speed of the application (since only HTML is loaded on the client side.)
- The applicaton uses an application factory, which will allow us to extend it further (add more endpoints, integrate databases, etc) at a later date. This also allows us to use pytest to test our application using the built in test client from Werkzeug.

### Security Considerations

The biggest concern for this application is the use of user provided input into the application. There are two possible vulnerabilities here:

The first is Cross-Site Scripting (XSS). A user could theoretically store malicious code in a field (such as the username field) which could trigger malicious code to run (and steal data from our application, for example). Normally this is done through specially crafted javascript code. In this application, Jinja handles most of the cases for XSS by automatically escaping all values inserted into the HTML. However, in order to prevent against other types of attacks (such as using `javascript:` URIs in a `a` tags `href` attribute) we need to also set the Content-Security-Policy Header in Flask to prevent the browser from loading and running scripts from unauthorized resources. For the purposes of this application, the CSP header has been set to:

    `response.headers['Content-Security-Policy'] = "default-src 'self'"`

which prevents code from any other site except our site from being executed. 

In addition, we also need to worry about Cross Site Request Forgery attacks. This is where an attacker can submit data to our application from a different site (possibly to trick a user into entering their credentials on a page they control). To protect against this, our application generates a unique token (called a csrf_token) which is attached to any form when the user `GET`s the page. On a `POST` this field is submitted and checked against the backend to make sure it matches (and has not expired or been tampered with). If the token is valid, the submission will go through. Otherwise the validation of the request fails.

This is done using the CSRFProtect class, provided by WTForms. This automatically generates the CSRF Token and checks it on POST to ensure it is valid. 

The final concern with regards to user input is the use of a binary on the CLI. This is not currently handled by this version of the application, but since we are passing user input directly into the application, it could be possible to call a different application based on the user input and compromise the underlying server. This would require some additional investigation and a POC to validate and implement a fix.

Some addititional headers that have been added in to each response (using the `after_request` hook for flask):
    - X-Content-Type-Options - Prevent XSS abuse based on browser guessing the content-type of the response
    - X-Frame-Options - Prevent our site from being loaded in an iframe (clickjacking attacks)
    - X-XSS-Protection - Prevent loading of the page if the request contains possible javascript code and the response contains the same data.
    - Set-Cookie - Cookies are set to HttpOnly to prevent them from being read by javascript, Lax to prevent submitting CSRF-prone requests from external sites, and Secure is set to false because the autograder may not support HTTPS for the application (but it would be ideal to set this to True.)

### Next Steps

- The design of the application could be improved (no css was used). 
- Need to investigate the use of subprocess within the application to make sure it does not provide a path to compromise the underlying host. 
- Session management should use expiration to prevent users from staying logged in.
- There should be a logout endpoint to allow users to logout of there account
- Tests should be written to test the security functionality. Tools such as webtest would allow us to simulate a browser and not need to disable CSRF to run some of our tests. 