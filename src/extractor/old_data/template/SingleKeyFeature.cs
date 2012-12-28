using System;
using System.Collections.Generic;

namespace KeyLoggerFeatureExtractor
{
    class SingleKeyFeature
    {
        /// <summary>
        ///     Total times for key presses
        /// </summary>
        public long total_time;

        /// <summary>
        ///     Keep track of each keys total fly time
        /// </summary>
        public long total_fly;

        /// <summary>
        ///     Total clicks for key presses
        /// </summary>
        public long total_clicks;

        /// <summary>
        ///     The total down times for calcuating standard deviation
        /// </summary>
        public List<long> times;

        /// <summary>
        ///     The total fly times for calculating standard deviation
        /// </summary>
        public List<long> flies;

        /// <summary>
        ///     The shortest amount of down time
        /// </summary>
        public long min_time;

        /// <summary>
        ///     The longest amount of down time
        /// </summary>
        public long max_time;

        /// <summary>
        ///     The shortest amount of fly time
        /// </summary>
        public long min_fly;

        /// <summary>
        ///     The longest amount of fly time
        /// </summary>
        public long max_fly;

        /// <summary>
        ///     Default constructor to set the variables
        /// </summary>
        public SingleKeyFeature()
        {
            // Set totals to zero
            this.total_clicks = 0;
            this.total_fly = 0;
            this.total_time = 0;

            // Create new lists to store all times
            this.times = new List<long>();
            this.flies = new List<long>();

            // Set mins and maxs to long.Max and Min values
            this.min_fly = long.MaxValue;
            this.max_fly = long.MinValue;
            this.min_time = long.MaxValue;
            this.max_time = long.MinValue;
        }


        /// <summary>
        ///     Get the average fly time
        /// </summary>
        /// <returns>The average fly time as a double</returns>
        public double GetAverageFly()
        {
            return (double)total_fly / total_clicks;
        }
        
        /// <summary>
        ///     Get the average down time
        /// </summary>
        /// <returns>The average down time as a double</returns>
        public double GetAverageDown()
        {
            return (double)total_time / total_clicks;
        }

        /// <summary>
        ///     Get the standard deviation for down time
        /// </summary>
        /// <returns>The standard deviation as a double</returns>
        public double GetDownStandardDeviation()
        {
            double num = 0;
            
            for (int i = 0; i < times.Count; i++)
            {
                num += Math.Pow(times[i] - GetAverageDown(), 2);
            }

            Console.WriteLine("TIMES COUNT = " + times.Count);
            return Math.Sqrt(num / times.Count);
        }

        public double GetFlyStandardDeviation()
        {
            double num = 0;

            for (int i = 0; i < flies.Count; i++)
            {
                num += Math.Pow(flies[i] - GetAverageFly(), 2);
            }

            return Math.Sqrt(num / flies.Count);
        }
    }
}
