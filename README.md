# XSSStrike-NG

## Description

**XSSStrike-NG** is a BurpSuite plugin that facilitates the rapid and intense identification of Cross-Site Scripting (XSS) vulnerabilities.

This plugin assists the pentester by automating certain tasks to provide a quick overview of XSS exploitability.

## Features

### DOM-XSS
- Static analysis in passive mode

### REFLECTED-XSS
**EntryPoints Identification**: In active mode, it searches for potential injection points in HTTP requests.

**Context Identification**: Uses context-based payloads for the injection.

## Requirements

- [Jython Standalone](https://www.jython.org/download.html)

## Installation

To install the plugin, follow these steps:

1. Configure the Jython path in BurpSuite:

![install_1](./install_1.png)

2. Install the plugin in BurpSuite:

![install_2](./install_2.png)

## Usage

To use the plugin, follow these steps:

1. Select the request or site and initiate the active scan in Burp.

![usage_1](./uso_1.png)

## Contributions
- Suggest a feature

- Report a bug

- Fix something and open a pull request

## License

Licensed under the GNU GPLv3, see LICENSE for more information.
