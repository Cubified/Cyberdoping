# Raw File Fuzzer

A simple fuzzer application for finding bugs in ThermoRawFileParser.dll, Thermo Fisher's official `.RAW` file parser.

## Compiling and Running

First, install Visual Studio.  Then open `RawFileFuzzer.sln`.  The latest version of [mzLib](https://github.com/smith-chem-wisc/mzLib) should install automatically, but if not it can be done via Nuget.

Build the solution, then run it via:

```sh
$ .\RawFileFuzzer\bin\x64\Debug\net8.0\RawFileFuzzer.exe
```

The fuzzer expects a valid `.RAW` file to exist at `C:\Xcalibur\examples\data\steroids02.raw`.  If [Xcalibur](https://www.thermofisher.com/us/en/home/industrial/mass-spectrometry/liquid-chromatography-mass-spectrometry-lc-ms/lc-ms-software/lc-ms-data-acquisition-software/xcalibur-data-acquisition-interpretation-software.html) is installed, it will be present.
