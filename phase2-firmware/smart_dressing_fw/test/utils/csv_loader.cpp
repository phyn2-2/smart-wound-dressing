#include "csv_loader.h"
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <iostream>

std::vector<SensorReading> load_csv(const std::string& path) {
    std::ifstream file(path);

    if (!file.is_open()) {
        throw std::runtime_error("Failed to open CSV file: " + path);
    }

    std::vector<SensorReading> readings;
    std::string line;

    // Skip header line
    if (!std::getline(file, line)) {
        throw std::runtime_error("CSV file is empty: " + path);
    }

    // Parse data lines
    while (std::getline(file, line)) {
        // Skip empty lines
        if (line.empty()) {
            continue;
        }

        std::stringstream ss(line);
        std::string token;
        SensorReading reading;

        // Parse time_hours
        if (!std::getline(ss, token, ',')) {
            throw std::runtime_error("Malformed CSV line (missing time_hours): " + line);
        }
        reading.time_hours = std::stof(token);

        // Parse pH
        if (!std::getline(ss, token, ',')){
            throw std::runtime_error("Malformed CSV line (missing pH): " + line);
        }
        reading.pH = std::stof(token);

        // Parse temperature
        if (!std::getline(ss, token, ',')) {
            throw std::runtime_error("Malformed CSV line (missing temp): " + line);
        }
        reading.temp = std::stof(token);

        readings.push_back(reading);
    }

    file.close();

    if (readings.empty()) {
        throw std::runtime_error("No data rows found in CSV: " + path);
    }

    std::cout << "Loaded " << readings.size() << "readings from " << path << std::endl;

    return readings;
}

