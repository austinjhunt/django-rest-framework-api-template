# Django Project Template

This repo contains a template Django project with templated logic for authentication, password management, [Stripe](https://stripe.com) payment processing, profile editing, [Google ReCAPTCHA](https://www.google.com/recaptcha/about/) token verification, [AWS Cloudwatch](https://aws.amazon.com/cloudwatch/) logging, [Slack](https://slack.com/) webhook-driven error alerting, [Sentry](https://sentry.io) monitoring, and more. It contains pre-written tests for authentication, password management, and profile (user model extension) management.

## Logging

It contains [middleware](./src/api/middleware/logging.py) that logs all incoming requests.

All logging is done in a standard JSON format, e.g.,

```python
logger.info({
    'action': 'ViewName.methodName',
    'arg1': arg1Value,
    'arg2': arg2Value
})

...
except Exception as e:
    logger.error({
        'action': 'ViewName.methodName',
        'error': str(e)
    })

```

## Primary Use Case

You can use this template as a foundation for a Django REST Framework API that uses token-based authentication.

## Using the Template

Clone the repository. Copy the sample environment variable file [`.env-sample`](./src/project/.env-sample) to your own `.env` file in the same directory and replace the `CHANGEME` values in the file with values specific to your project.
