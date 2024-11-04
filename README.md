# baestatement

a parser for BankAustria e-Statement PDF files.

## Installation

- install `pdftohtml` from the `poppler` (Arch) or `poppler-utils` (Debian/Ubuntu) package
- run `pipx install git+https://github.com/Ferdi265/baestatement` to install
- run `pipx install --editable .` for a development install

## Features

- `bae-show`: Parse and display BankAustria e-Statement PDFs in a text-based format.
- `bae-dump`: Dump BankAustria e-Statement PDFs as Python expression.
- `bae-csv`: Convert BankAustria e-Statement PDFs to CSV.

Small proof-of-concept library and tools for working with BankAustria
e-Statement PDFs.

Future versions will potentially support more formats, categorization,
filtering, etc..., if I ever get to expanding this.
