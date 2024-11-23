# FreeDope:  Doping Suppression

This repository is a proof-of-concept attack on Thermo Fisher's [FreeStyle](https://www.thermofisher.com/us/en/home/technical-resources/technical-reference-library/mass-spectrometry-support-center/liquid-chromatography-mass-spectrometry-software-support/freestyle-software-support/freestyle-software-support-getting-started.html) mass spectrometry analysis software.

It scans for `.RAW` files in a directory, compares them using a k-nearest neighbors classifier, and swaps in clean data if a specific athlete is detected.
