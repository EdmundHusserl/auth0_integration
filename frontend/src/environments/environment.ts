/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://172.30.10.126:5000', // the running FLASK api server url
  auth0: {
    url: 'secure-app-trust-me.us', // the auth0 domain prefix
    audience: 'http://localhost:5000', // the audience set for the auth0 app
    clientId: 'Po6Ec8jqb5vKsLsZ1yagnBRzwhzQP9hi', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application. 
  }
};