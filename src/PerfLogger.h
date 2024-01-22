/*
 * HPCGPT
 * @author  : nevakrien+gpt4
 *
 */
#ifndef PERFLOGGER_H
#define PERFLOGGER_H

#include <chrono>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>

#include <iostream>


// Check if NEVA_TIME_BENCHMARK is defined
#ifdef NEVA_TIME_BENCHMARK


namespace LogEvents {
    constexpr const char* Start = "Start";
    constexpr const char* End = "End";
    constexpr const char* OutputFile = "perf_output.txt";
    // Add more event names as needed
}

class PerfLogger {
public:
    static PerfLogger& getInstance() {
        static PerfLogger instance;
        return instance;
    }

    void logEvent(const char* eventName) {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();
        std::stringstream logEntry;
        logEntry << "Event: " << eventName << " at " << duration << " ms";
        logBuffer.push_back(logEntry.str());

        // Debug print
        //std::cerr << "Logged event: " << logEntry.str() << std::endl;
    }

    ~PerfLogger() {
        writeToDisk(LogEvents::OutputFile);
        // Debug print
        //std::cerr << "Destructor called, writing log to disk." << std::endl;
    }

private:
    std::chrono::time_point<std::chrono::high_resolution_clock> startTime;
    std::vector<std::string> logBuffer;
    PerfLogger() {
        startTime = std::chrono::high_resolution_clock::now();
    }

    void writeToDisk(const char* filePath) {
        std::cerr << "Attempting to write to disk at " << filePath << "..." << std::endl; // Debug print
        std::ofstream logFile(filePath, std::ios::app);
        if (logFile.is_open()) {
            for (const auto& entry : logBuffer) {
                logFile << entry << std::endl;
            }
            logFile.close();
            std::cerr << "Log written to " << filePath << std::endl; // Debug print
        } else {
            std::cerr << "Unable to open log file at " << filePath << std::endl; // Error message
        }
    }
};


#define LOG_EVENT(event) PerfLogger::getInstance().logEvent(event)

#else


#define LOG_EVENT(event)

#endif // NEVA_TIME_BENCHMARK

#endif // PERFLOGGER_H
