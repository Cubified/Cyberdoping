# FreeDope:  Doping Suppression via Analysis Software Manipulation

This repository is a proof-of-concept attack on Thermo Fisher's [FreeStyle](https://www.thermofisher.com/us/en/home/technical-resources/technical-reference-library/mass-spectrometry-support-center/liquid-chromatography-mass-spectrometry-software-support/freestyle-software-support/freestyle-software-support-getting-started.html) mass spectrometry analysis software.

It scans for `.RAW` files in a directory, compares them using a k-nearest neighbors classifier, and swaps in clean data if a specific athlete is detected.

## Running

First, ensure that at least one of Python 3.9, 3.10, or 3.11 is installed.  This is because [pyopenms](https://pyopenms.readthedocs.io/en/latest) has only published releases for these specific versions.

If running on Linux or macOS, ensure that [Wine](https://winehq.org) is installed.  This should only be for debugging purposes, because FreeStyle cannot run on non-Windows machines.

Then (assuming Python 3.11):

```sh
$ git clone git@github.com:Cubified/FreeDope.git
$ cd FreeDope
$ pip3.11 install -r requirements.txt
$ python3.11 prep.py --train
$ python3.11 detector.py /path/to/raw/files
```

Where `/path/to/raw/files` is anywhere Thermo Fisher .RAW files are located (e.g. `C:\Xcalibur\example\data`)
