# DataCite Linked Data Publication Namespace

This repository publishes the TIB-maintained DataCite linked-data vocabulary
bundle for GitHub Pages.

- Canonical persistent namespace: `https://w3id.org/tib/datacite/`
- GitHub Pages backend: `https://tibhannover.github.io/datacite/`
- Source toolkit: `TIBHannover/datacite-metadata-toolkit`

The files in this repository are generated publication artifacts. Make vocabulary
source changes in the toolkit, regenerate the production namespace bundle there,
then copy the generated bundle into this repository.

## Directory Layout

```text
class/       RDF class definitions
property/    RDF property definitions
vocab/       SKOS concept schemes and controlled terms
context/     JSON-LD contexts
manifest/    Versioned inventories and release matrix files
dist/        Bundled JSON-LD, Turtle, RDF/XML, and OWL distributions
```

Each section also includes an `index.html` page for browsing through GitHub
Pages.

## Regeneration Workflow

From the source toolkit checkout:

```bash
git switch w3id/prep
npm run build:production-namespace
```

Then copy the generated contents of `production-namespace/` to this repository
root and validate:

```bash
find . -type f | wc -l
rg -n --glob '!README.md' "schema\\.stage\\.datacite\\.org|schema\\.datacite\\.org/linked-data|datacite//|Linked Data \\(Staging\\)" .
```

The `rg` command should return no matches.

## Publishing Checklist

1. Commit the generated files in this repository.
2. Push to `TIBHannover/datacite`.
3. Enable GitHub Pages for the repository's `main` branch.
4. Confirm that `https://tibhannover.github.io/datacite/` serves the bundle.
5. Add or update the corresponding `perma-id/w3id.org` redirect rules for
   `https://w3id.org/tib/datacite/`.
