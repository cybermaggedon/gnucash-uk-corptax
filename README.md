
# `gnucash-uk-corptax`

## Introduction

This is a utility which takes a UK corporation tax return formatted using
[`gnucash-ixbrl`](https://github.com/cybermaggedon/gnucash-ixbrl) and
submits in accordance with the HMRC Corporation Tax filing API.

`gnucash-uk-corptax` presently understands a small subset of the corporation
tax submission.  It might be useful for a small business with simple tax
affairs.  It really is no use to a complex business.

## Status

This is a command-line utility, which has been tested with the HMRC test API.

## Credentials

In order to use this, you need production credentials (vendor ID, username,
password) for the Corporation Tax API.  HMRC does not permit these
credentials to be shared publicly.

Developer hub: 
https://developer.service.hmrc.gov.uk/api-documentation/docs/using-the-hub

## Installing

```
pip3 install git+https://github.com/cybermaggedon/gnucash-uk-corptax
```

## Testing

There is a corptax emulator here.  Run:

```
corptax-test-service
```

To submit the test account data to the test service:

```
gnucash-uk-corptax -c config.json -a accts.html -t ct600.html
```

Output should look like this:
```
IRmark is hOgMwO+75eJbBax/OhPZy/NszxE=
Correlation ID is 1E242
Endpoint is http://localhost:8082/
Poll time is 1.0
Poll...
Poll...
Poll...
Poll...
Submitted successfully.
Delete request...
Completed.
```

The two files `accts.html` and `ct600.html` included in this repo
are sample accounts which were output from `gnucash-ixbrl`.

## Usage

```
usage: gnucash-uk-corptax [-h] [--config CONFIG] --accounts ACCOUNTS
                          --computations COMPUTATIONS [--show-ct]

Submittion to HMRC Corporation Tax API

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Configuration file (default: config.json)
  --accounts ACCOUNTS, -a ACCOUNTS
                        Company accounts iXBRL file
  --computations COMPUTATIONS, --ct600 COMPUTATIONS, -t COMPUTATIONS
                        Corporation tax computations iXBRL file
  --show-ct, -p         Just output submission message, without submit step
```

The configuration file is a JSON file, should look something like this:

```
{
    "company-type": 6,
    "declaration-name": "Sarah McAcre",
    "declaration-status": "Director",
    "username": "CTUser100",
    "password": "password",
    "gateway-test": "1",
    "tax-reference": "1234123412",
    "vendor-id": "1234",
    "software": "gnucash-uk-corptax",
    "software-version": "0.0.1",
    "url": "http://localhost:8081/",
    "title": "Ms",
    "first-name": "Sarah",
    "second-name": "McAcre",
    "email": "sarah@example.org",
    "phone": "447900123456"
}
```

The accounts file is an iXBRL-formatted company accounts file.  The
computations file is an iXBRL-formatted corporation tax computations.

Corporation tax data is read from the corporation tax computations, and
used to construct the GovTalkMessage containing corporation tax submission
and account information.  This is submitted to the corporation tax
endpoint.

## What it does

# Licences, Compliance, etc.

## Warranty

This code comes with no warranty whatsoever.  See the [LICENSE](LICENCE) file
for details.  Further, I am not an accountant.  It is possible that this code
could be useful to you in meeting regulatory reporting requirements for your
business.  It is also possible that the software could report misleading
information which could land you in a lot of trouble if used for regulatory
purposes.  Really, you should check with a qualified accountant.

## Licence

Copyright (C) 2020, 2021, Cyberapocalypse Limited

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

