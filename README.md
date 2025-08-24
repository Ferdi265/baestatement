# baestatement

a parser for BankAustria e-Statement PDF files.

## Installation

- install `pdftohtml` from the `poppler` (Arch) or `poppler-utils` (Debian/Ubuntu) package
  - NOTE! since version `poppler 25.07.0`, Bank Austria e-Statement PDF files
    are no longer correctly converted to HTML by `pdftohtml`, breaking this package.
- run `pipx install git+https://github.com/Ferdi265/baestatement` to install
- run `pipx install --editable .` for a development install

## Features

- `bae-show`: Parse and display BankAustria e-Statement PDF or JSON files in a text-based format.
- `bae-plot`: Plot information from BankAustria e-Statement PDF or JSON files.
- `bae-dump`: Dump BankAustria e-Statement PDFs as Python expression.
- `bae-csv`: Convert BankAustria e-Statement PDFs to CSV.
- `bae-json`: Convert BankAustria e-Statement PDFs to JSON.

Small proof-of-concept library and tools for working with BankAustria
e-Statement PDFs.

Future versions will potentially support more formats, categorization,
filtering, etc..., if I ever get to expanding this.
