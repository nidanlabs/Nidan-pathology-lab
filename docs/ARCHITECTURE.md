# NIDAN Architecture

NIDAN will keep upstream SENAITE packages separate from NIDAN-specific customization.

## Layers
1. SENAITE/Plone platform
2. SENAITE LIMS packages
3. `custom/nidan.lims` domain customizations
4. Deployment configuration

## Principle
Do not merge independent Python packages into one source tree. Preserve package boundaries so upgrades and maintenance remain manageable.
