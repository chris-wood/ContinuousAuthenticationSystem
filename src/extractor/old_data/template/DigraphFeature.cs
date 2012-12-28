using System;
using System.Collections.Generic;

namespace KeyLoggerFeatureExtractor
{
    class DigraphFeature
    {
        long minTime = long.MaxValue;
        long maxTime = long.MinValue;
        List<long> times = new List<long>();

        /**
         * Add a time to the times list
         *
         * @params time Time to be added to the list
         */
        public void addTime(long time)
        {
            if (time > maxTime) maxTime = time;
            if (time < minTime) minTime = time;
            times.Add(time);
        }

        /**
         * Returns the average of the times
         * in the time list
         */
        public double getAverage()
        {
            long total = 0;
            foreach (long value in times)
            {
                total += value;
            }
            return ((double)total / times.Count);
        }

        /**
         * Return the standard deviation of 
         * the times for this digram
         */
        public double getStandardDeviation()
        {
            long numerator = 0;
            double avg = getAverage();

            foreach (long value in times)
            {
                numerator += (long)Math.Pow(value - avg, 2);
            }

            return (Math.Sqrt((numerator / times.Count)) * 100 / 100);
        }

        public long getMin()
        {
            return minTime;
        }

        public long getMax()
        {
            return maxTime;
        }
    }
}
