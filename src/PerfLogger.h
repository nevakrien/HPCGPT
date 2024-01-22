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
#include <forward_list>
#include <sstream>

#include <iostream>


// Check if NEVA_TIME_BENCHMARK is defined
#ifdef NEVA_TIME_BENCHMARK


//convention dont put any spaces in the name or new lines python parses based on those
namespace LogEvents {
    constexpr const char* Start = "Started program";
    constexpr const char* End = "Ended program";
    
    constexpr const char* MultiStart = "Started MultiHeadAttention";
    constexpr const char* MultiEnd = "Ended MultiHeadAttention";

    constexpr const char* BlockStart = "Started transformerBlock";
    constexpr const char* BlockEnd = "Ended transformerBlock";

    constexpr const char* FFStart = "Started feadForward";
    constexpr const char* FFEnd = "Ended feadForward";

    constexpr const char* NormStart = "Started layerNorm";
    constexpr const char* NormEnd = "Ended layerNorm";

    constexpr const char* OutputFile = "code_perf_output.txt";
    // Add more event names as needed
}

class PerfLogger {
public:
    struct LogEntry {
        std::string eventName;
        long long duration; // Duration in nanoseconds
    };

    static PerfLogger& getInstance() {
        static PerfLogger instance;
        return instance;
    }

    void logEvent(const char* eventName) {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(now - startTime).count();
        logBuffer.push_front({eventName, duration});
    }

    ~PerfLogger() {
        writeToDisk(LogEvents::OutputFile);
    }

private:
    std::chrono::time_point<std::chrono::high_resolution_clock> startTime;
    std::forward_list<LogEntry> logBuffer;
    PerfLogger() : startTime(std::chrono::high_resolution_clock::now()) {}

    void writeToDisk(const char* filePath) {
        std::ofstream logFile(filePath, std::ios::app);
        if (logFile.is_open()) {
            logBuffer.reverse(); // Reverse the list before writing
            for (const auto& entry : logBuffer) {
                logFile<< entry.eventName << " " << entry.duration << std::endl;
            }
            logFile.close();
        } else {
            std::cerr << "Unable to open log file at " << filePath << std::endl;
        }
    }
};


#define LOG_EVENT(event) PerfLogger::getInstance().logEvent(event)

#else


#define LOG_EVENT(event)

#endif // NEVA_TIME_BENCHMARK

#endif // PERFLOGGER_H
