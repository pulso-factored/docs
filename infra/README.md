# Pulso infrastructure

Technical documentation for the separate Terraform repository that owns Pulso's deployable AWS foundation. The application repository owns its local Podman/LocalStack development environment; this repository owns cloud infrastructure code. It is not a second implementation of the Improvement Engine.

## Guide

- [Infrastructure, reliability and observability](guide/infrastructure-and-observability.md): repository boundaries, environment layout, reliability controls, monitoring and Langfuse forwarding, with evidence-based notes about what is and is not deployed.

## Important operational boundary

Terraform files describe desired infrastructure; their presence does not prove that a plan was applied or that a service is live. Read the guide and the current [`pulso-factored/infra`](https://github.com/pulso-factored/infra) default branch before running Terraform. In particular, inspect the selected root/module, workspace/backend, account, region and environment variables before any plan or apply. This documentation does not authorize deployment.

The intended long-term environments are staging and production, with production serving the demo. Deployment automation is not enabled by this documentation. Never put secret values in this repository; configure them through the approved secret-management path.
