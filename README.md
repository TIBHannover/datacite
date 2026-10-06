# DataCite Linked Data Publication Namespace

This repository publishes the TIB-maintained DataCite linked-data vocabulary
bundle for GitHub Pages.

- Canonical persistent namespace: `https://w3id.org/tib/datacite/`
- GitHub Pages backend: `https://tibhannover.github.io/datacite/`
- Source toolkit: `TIBHannover/datacite-metadata-toolkit`

The files in this repository are generated publication artifacts. Make vocabulary
source changes in the toolkit, regenerate the production namespace bundle there,
then sync the generated bundle into this repository with a pull request.

## Directory Layout

```text
class/       RDF class definitions
property/    RDF property definitions
vocab/       SKOS concept schemes and controlled terms
context/     JSON-LD contexts
manifest/    Versioned inventories and release matrix files
dist/        Bundled JSON-LD, Turtle, RDF/XML, and OWL distributions
mappings/    Crosswalk mapping sets (SSSOM, JSKOS, SKOS) and the crosswalk guide
```

Each section also includes an `index.html` page for browsing through GitHub
Pages.

## Generated File Counts

Counts include generated JSON-LD, HTML, and context files currently present in
each directory. The sync workflow refreshes this table when it opens a
publication pull request.

| Directory | Files |
| --- | ---: |
| `class/` | 43 |
| `property/` | 161 |
| `vocab/` | 339 |
| `vocab/` direct files | 2 |
| `vocab/contributorType/` | 47 |
| `vocab/dateType/` | 27 |
| `vocab/descriptionType/` | 15 |
| `vocab/funderIdentifierType/` | 13 |
| `vocab/identifierType/` | 5 |
| `vocab/nameType/` | 7 |
| `vocab/numberType/` | 11 |
| `vocab/relatedIdentifierType/` | 49 |
| `vocab/relationType/` | 81 |
| `vocab/resourceTypeGeneral/` | 71 |
| `vocab/titleType/` | 11 |

## License

The generated vocabulary and publication artifacts in this repository are
licensed under the Creative Commons Attribution 4.0 International license
(`CC-BY-4.0`). See [LICENSE](LICENSE).

The source toolkit used to generate these artifacts is maintained separately in
`TIBHannover/datacite-metadata-toolkit`; its code and tooling are licensed as
`Apache-2.0`.

## Regeneration Workflow

From the source toolkit checkout:

```bash
git switch main
npm run build:production-namespace
```

The generated `production-namespace/` bundle is synchronized into this
publication repository by the `Sync production namespace` GitHub Actions
workflow. Run the workflow from this repository and set `source_ref` to the
toolkit branch, tag, or commit to publish. The workflow opens a pull request
that copies only these generated paths:

```text
production-namespace/class/    -> class/
production-namespace/property/ -> property/
production-namespace/vocab/    -> vocab/
production-namespace/context/  -> context/
production-namespace/manifest/ -> manifest/
production-namespace/dist/     -> dist/
production-namespace/CHECKSUMS.sha256 -> CHECKSUMS.sha256
```

Repository-owned root files such as `.nojekyll`, `LICENSE`, `README.md`, and
`index.html` are not overwritten by the sync workflow.

The workflow uses this repository's built-in `GITHUB_TOKEN`. Repository Actions
settings must allow read and write permissions, and must allow GitHub Actions to
create pull requests.

The workflow validates the generated checksums before opening a pull request.
After reviewing the PR, validate the merged publication tree:

```bash
find . -type f | wc -l
rg -n --glob '!README.md' "schema\\.stage\\.datacite\\.org|schema\\.datacite\\.org/linked-data|datacite//|Linked Data \\(Staging\\)" .
```

The `rg` command should return no matches.

## Publishing Checklist

1. Run the `Sync production namespace` workflow in this repository.
2. Review and merge the generated sync pull request.
3. Confirm that GitHub Pages is enabled for this repository's `main` branch.
4. Confirm that `https://tibhannover.github.io/datacite/` serves the bundle.
5. Add or update the corresponding `perma-id/w3id.org` redirect rules for
   `https://w3id.org/tib/datacite/`.
