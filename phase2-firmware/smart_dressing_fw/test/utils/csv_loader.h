#ifndef CSV_LOADER_H
#define CSV_LOADER_H

#include <string>
#include <vector>

/**
 * @brief Simple sensor reading structure for CSV replay
 */
struct SensorReading {
    float time_hours;
    float pH;
    float temp;
};

/**
 *
 * Expected CSV format:
 * time_hours,pH,temp
 * 0.0,7.1,36.8
 * 0.25,7.2,36.9
 *
 * @param path Absolute or relative path to CSV file
 * @return Vector of sensor readings in chronological order
 * @throws std::runtime_error if file cannot be opened or parsed
 */
std::vector<SensorReading> load_csv(const std::string& path);

#endif // CSV_LOADER_H
