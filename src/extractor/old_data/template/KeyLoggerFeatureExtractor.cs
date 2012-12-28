using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Text;

namespace KeyLoggerFeatureExtractor
{
    class KeyLoggerFeatureExtractor
    {
        /// <summary>
        ///     Key press queue <key code, down time>
        /// </summary>
        private Dictionary<int, long> queue = new Dictionary<int, long>();

        /// <summary>
        ///     Key code features
        /// </summary>
        private Dictionary<int, SingleKeyFeature> features = new Dictionary<int, SingleKeyFeature>();

        /// <summary>
        ///     Keep track of last press for the keys fly time
        /// </summary>
        private long last = 0;

        /// <summary>
        ///     The lowest key code cared about
        /// </summary>
        private int KEY_CODE_LOW = 1;

        /// <summary>
        ///     The highest key code cared about
        /// </summary>
        private int KEY_CODE_HIGH = 127;

        /// <summary>
        ///     The most common digraphs to check for
        /// </summary>
        private string[] DIGRAPHS = { "TH", "HE", "IN", "EN", "NT", "RE", "ER", "AN", "TI", "ES", "ON", "AT" };

        /// <summary>
        ///     Main program to extract features from log file and put them into a Weka file format
        /// </summary>
        /// <param name="args">args[0] = The log file to extract from, args[1] = The name of the output file to save to</param>
        public static void Main(string[] args)
        {
            if (args.Length < 2)
                Usage();

            string output = args[args.Length - 1];
            int count = args.Length - 1;

            // Create a new feature extractor
            KeyLoggerFeatureExtractor fe = new KeyLoggerFeatureExtractor();

            // Write the averages to the output file
            StreamWriter writer = new StreamWriter(output);

            // Write the first generic row of the output file
            StringBuilder sb = new StringBuilder();
            sb.Append("Name,");

            for (int i = fe.KEY_CODE_LOW; i <= fe.KEY_CODE_HIGH; i++)
            {
                sb.Append(i + "_down_min,");
                sb.Append(i + "_down_max,");
                sb.Append(i + "_down_avg,");
                sb.Append(i + "_down_std,");
                sb.Append(i + "_fly_min,");
                sb.Append(i + "_fly_max,");
                sb.Append(i + "_fly_avg,");
                sb.Append(i + "_fly_std,");
            }

            for (int i = 0; i < fe.DIGRAPHS.Length; i++)
            {
                string code = Convert.ToInt32(fe.DIGRAPHS[i][0]) + "" + Convert.ToInt32(fe.DIGRAPHS[i][1]);
                
                sb.Append(
                    code + "_min," +
                    code + "_max," +
                    code + "_avg," +
                    code + "_std,"
                );
            }

            writer.WriteLine(sb.ToString().Substring(0, sb.Length - 1));

            // Generate a row in the output file for each input file
            for (int i = 0; i < count; i++)
            {
                // Write the line with the file name as an identifier
                writer.WriteLine(
                    args[i] + "," + 
                    fe.GenerateSingleKeyReportFromLogFile(args[i])
                    // caw: took out this stuff
                    // + "," + 
                    //fe.GenerateDigraphReportFromLogFile(args[i])
                );
            }

            // Force a flush and close
            writer.Flush();
            writer.Close();
        }

        /// <summary>
        ///     Print the usage of the program and exit
        /// </summary>
        public static void Usage()
        {
            Console.Error.WriteLine("Usage: KeyLoggerFeatureExtractor.exe <logfiles> <outputfile>");
            Environment.Exit(1);
        }

        /// <summary>
        ///     Default contructor prevention
        /// </summary>
        public KeyLoggerFeatureExtractor()
        {
        }

        /// <summary>
        ///     Generate the report and save to the output file
        /// </summary>
        /// <param name="log">The name of the log file</param>
        private string GenerateSingleKeyReportFromLogFile(string log)
        {
            // Create a string builder to return the row
            StringBuilder sb = new StringBuilder();

            try
            {
                // Create a file reader
                StreamReader reader = new StreamReader(log);
                string line;

                // Read the file until the end
                while ((line = reader.ReadLine()) != null)
                {
                    // Split on space (should always have 3)
                    string[] args = line.Split(' ');

                    // verify for all 3 args
                    if (args.Length == 3)
                    {
                        // Parse the args for easy use
                        long time = long.Parse(args[0]);
                        int key = int.Parse(args[1]);

                        // Ignore the key press action (args[2])

                        // Check to see if the key code is in the queue
                        if (queue.ContainsKey(key))
                        {
                            // If the key is in the queue calculate the time down
                            long total = time - queue[key];

                            // If the key hasn't been clicked yet
                            if (!features.ContainsKey(key))
                                features.Add(key, new SingleKeyFeature());

                            // Increment the clicks and add totals
                            features[key].total_time += total;
                            features[key].total_fly += (last != 0) ? time - last : 0;
                            features[key].total_clicks++;

                            // Add the times to the storage variables
                            features[key].times.Add(total);
                            features[key].flies.Add(time - last);

                            // Check the fly min and max
                            features[key].min_fly = ((time - last) < features[key].min_fly) ?
                                (time - last) : features[key].min_fly;

                            features[key].max_fly = ((time - last) > features[key].max_fly) ?
                                (time - last) : features[key].max_fly;

                            // Check the down min and max
                            features[key].min_time = (total < features[key].min_time) ?
                                (total) : features[key].min_time;

                            features[key].max_time = (total > features[key].max_time) ?
                                (total) : features[key].max_time;
                        
                            // Remove that key from the queue
                            queue.Remove(key);
                        }
                        else
                        {
                            // The key press is down and we need to add the time
                            queue.Add(key, time);
                        }

                        // Store the key press time
                        last = time;
                    }
                }

                // Close the reader
                reader.Close();

                // Iterate over all common key characters
                for (int i = KEY_CODE_LOW; i <= KEY_CODE_HIGH; i++)
                {
                    // If the key was pressed, add the value
                    if (features.ContainsKey(i))
                        sb.Append(
                            features[i].min_time + "," +
                            features[i].max_time + "," +
                            features[i].GetAverageDown() + "," +
                            features[i].GetDownStandardDeviation() + "," +
                            features[i].min_fly + "," +
                            features[i].max_fly + "," +
                            features[i].GetAverageFly() + "," +
                            features[i].GetFlyStandardDeviation() + "," + "\n"
                        );
                    else
                    {
                        sb.Append("0,0,0,0,0,0,0,0,\n");
                    }
                }
            }
            catch
            {
                Console.Error.WriteLine("Error... exiting program.");
                Environment.Exit(1);
            }

            return sb.ToString().Substring(0, sb.Length - 1);
        }

        /// <summary>
        ///     Generate the report and save to the output file
        /// </summary>
        /// <param name="log">The name of the log file</param>
        private string GenerateDigraphReportFromLogFile(string log)
        {
            // The string builder used to generate output file
            StringBuilder sb = new StringBuilder();

            //Map Key: digraph, Value: stats about this digraph;
            Dictionary<string, DigraphFeature> digraphs = new Dictionary<string, DigraphFeature>();

            //Map Key: character, Value: Time key was pressed down
            Dictionary<char, long> downTimes = new Dictionary<char, long>();

            //Mapping of keycodes to characters
            Dictionary<int, char> numberToChar = new Dictionary<int, char>();

            //List of nost common 12 digrams
            // Line read from file
            string line;

            // array of last two charachters typed
            char[] digraphChar = new char[2];

            // The string of the last two characters typed
            string digraphString = "";

            /**
            * Initialize numberToChar map
            */
            for (int i = 65; i <= 90; i++)
            {
                numberToChar.Add(i, (char)i);
            }

            StreamReader file = new StreamReader(log);

            while ((line = file.ReadLine()) != null)
            {
                string[] values = line.Split();
                long time = long.Parse(values[0]);
                int keyCode = int.Parse(values[1]);
                string keyStatus = values[2];

                if (keyStatus == "KEY_DOWN" && numberToChar.ContainsKey(keyCode))
                {
                    // Appent most recent character to the digraph
                    digraphChar[1] = (char)keyCode;

                    // convert new digraph to a string
                    digraphString = new string(digraphChar);

                    digraphChar[0] = digraphChar[1];
                    if (downTimes.ContainsKey(digraphChar[1]))
                    {
                        downTimes[digraphChar[1]] = time;
                    }
                    else
                    {
                        downTimes.Add(digraphChar[1], time);
                    }
                }
                /*
                 * If the key is released find how long
                 * it took to press the digraph
                 */
                else if (keyStatus == "KEY_UP" && (Array.IndexOf(DIGRAPHS,digraphString) > -1))
                {
                    if (digraphs.ContainsKey(digraphString))
                    {
                        digraphs[digraphString].addTime(time - downTimes[digraphString[0]]);
                    }
                    else
                    {
                        DigraphFeature info = new DigraphFeature();
                        digraphs.Add(digraphString, info);
                        digraphs[digraphString].addTime(time - downTimes[digraphString[0]]);
                    }
                }
            }


            for (int i = 0; i < DIGRAPHS.Length; i++)
            {
                if (digraphs.ContainsKey(DIGRAPHS[i]))
                {
                    sb.Append(
                        digraphs[DIGRAPHS[i]].getMin() + "," +
                        digraphs[DIGRAPHS[i]].getMax() + "," +
                        digraphs[DIGRAPHS[i]].getAverage() + "," +
                        digraphs[DIGRAPHS[i]].getStandardDeviation() + ","
                    );
                }
                else
                {
                    sb.Append("0,0,0,0,");
                }
            }

            return sb.ToString().Substring(0, sb.Length - 1);
        }
    }
}
