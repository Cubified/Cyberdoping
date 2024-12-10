using System;
using System.IO;
using System.Linq;
using System.Text;
using Proteomics;
using MassSpectrometry;
using System.Xml.Serialization;
using Readers;

class MzLibFuzzer
{
    const int PERMUTE_CHANCE = 1;
    const int DELETE_CHANCE = 1;
    const int FUZZ_ITERS = 1000;
    const int CHUNK_SIZE = 10;

    const string groundTruthFile = "C:\\Xcalibur\\examples\\data\\steroids02.raw";
    const string fuzzingDir = "FuzzingFiles";

    static void Main(string[] args)
    {
        Console.WriteLine("Starting mzLib Fuzzer...");

        byte[] groundTruth = File.ReadAllBytes(groundTruthFile);

        bool[] failedFiles = new bool[FUZZ_ITERS];

        Directory.CreateDirectory(fuzzingDir);

        // Run fuzzing tests
        for (int j = 0; j < FUZZ_ITERS; j += CHUNK_SIZE)
        {
            Console.WriteLine($"<== START OF CHUNK {Math.Floor((decimal)j / (decimal)CHUNK_SIZE)} ==>");

            // Group into batches to avoid hogging disk
            for (int i = j; i < j + CHUNK_SIZE; i++)
            {
                string testFilePath = Path.Combine(fuzzingDir, $"test_{i}.raw");
                try
                {
                    GenerateRandomRawFile(testFilePath, ref groundTruth);
                    DoFuzzTest(testFilePath, i);
                    failedFiles[i] = true; // Successfully parsed (not wanted)
                }
                catch (Exception ex)
                {
                    failedFiles[i] = ex.Message.Contains("Error opening RAW file!");

                    if (failedFiles[i]) // Graceful failure (not wanted)
                    {
                        Console.WriteLine($"[Test {i}] Failed gracefully.");
                    }
                    else
                    {
                        Console.WriteLine($"[Test {i}] Exception encountered: {ex.Message}");
                    }
                }
            }

            int successCount = 0;
            for (int i = j; i < j + CHUNK_SIZE; i++)
            {
                if (failedFiles[i])
                {
                    // mzLib keeps file handles open until exit, attempt to delete
                    try
                    {
                        File.Delete(Path.Combine(fuzzingDir, $"test_{i}.raw"));
                    }
                    catch { }
                }
                else
                {
                    successCount++;
                }
            }

            Console.WriteLine($"<== END OF CHUNK {Math.Floor((decimal)j / (decimal)CHUNK_SIZE)} ({successCount} successes) ==>");
        }

        Console.WriteLine("Fuzzing completed.");
    }

    static void GenerateRandomRawFile(string filePath, ref byte[] groundTruth)
    {
        Random rand = new Random();
        byte[] randomData = new byte[groundTruth.Length];
        int effectiveLen = 0;

        for (int i = 0; i < groundTruth.Length; i++)
        {
            if (rand.Next(100) < PERMUTE_CHANCE)
            {
                randomData[effectiveLen++] = (byte)rand.NextInt64();
            }
            else if (rand.Next(100) < DELETE_CHANCE)
            {
                continue;
            }
            else
            {
                randomData[effectiveLen++] = groundTruth[i];
            }
        }

        // Use a FileStream to write data and ensure it is disposed
        using (FileStream fs = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None))
        {
            fs.Write(randomData, 0, effectiveLen);
        }
    }
    static void DoFuzzTest(string path, int i)
    {
        var msDataFile = ThermoRawFileReader.LoadAllStaticData(path);

        if (msDataFile == null)
        {
            Console.WriteLine($"[Test {i}] Failed to read file.");
            return;
        }

        // Fuzz key methods
        int numScans = msDataFile.NumSpectra;
        Console.WriteLine($"[Test {i}] Number of spectra: {numScans}");

        for (int scanIndex = 0; scanIndex < Math.Min(numScans, 10); scanIndex++) // Test the first 10 scans
        {
            try
            {
                var spectrum = msDataFile.GetOneBasedScan(scanIndex + 1);
                Console.WriteLine($"[Test {i}] Scan {scanIndex + 1}: {spectrum.MassSpectrum.Range}");
            }
            catch (Exception innerEx)
            {
                Console.WriteLine($"[Test {i}] Error processing scan {scanIndex + 1}: {innerEx.Message}");
            }
        }
    }
}