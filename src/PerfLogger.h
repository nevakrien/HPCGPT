/*
 * HPCGPT
 * @author  : nevakrien+gpt4
 *
 */
#ifndef PERFLOGGER_H
#define PERFLOGGER_H

//#include <chrono>
#include <time.h>
#include <fstream>
#include <string>
#include <forward_list>
#include <sstream>

#include <iostream>
#include <iomanip>

// Check if NEVA_TIME_BENCHMARK is defined
#ifdef NEVA_TIME_BENCHMARK


//convention dont put any spaces in the name or new lines python parses based on those
namespace LogEvents {
    constexpr const char* Start = "Started program";
    constexpr const char* End = "Ended program";

    constexpr const char* GptStart = "Started gpt2";
    constexpr const char* GptEnd = "Ended gpt2";

    constexpr const char* GenStart = "Started generate";
    constexpr const char* GenEnd = "Ended generate";
    
    constexpr const char* MultiStart = "Started MultiHeadAttention";
    constexpr const char* MultiEnd = "Ended MultiHeadAttention";

    constexpr const char* BlockStart = "Started transformerBlock";
    constexpr const char* BlockEnd = "Ended transformerBlock";

    constexpr const char* FFStart = "Started feadForward";
    constexpr const char* FFEnd = "Ended feadForward";

    constexpr const char* NormStart = "Started layerNorm";
    constexpr const char* NormEnd = "Ended layerNorm";

    constexpr const char* TensorMulStart = "Started Tensor::matmul";
    constexpr const char* TensorMulEnd = "Ended Tensor::matmul";

    constexpr const char* TensorTransMulStart = "Started Tensor::matmulTrans";
    constexpr const char* TensorTransMulEnd = "Ended Tensor::matmulTrans";

    constexpr const char* OutputFile = "code_perf_output.txt";
    // Add more event names as needed
}




class PerfLogger {
public:
    struct LogEntry {
        std::string eventName;
        timespec time;  // Using timespec for time measurement
    };

    static PerfLogger& getInstance() {
        static PerfLogger instance;
        return instance;
    }

    void logEvent(const char* eventName) {
        timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now); // Get the current time using clock_gettime
        logBuffer.push_front({eventName, now});
    }

    ~PerfLogger() {
        logEvent(LogEvents::End);
        writeToDisk(LogEvents::OutputFile);
    }



private:
    std::forward_list<LogEntry> logBuffer;
    PerfLogger() {
        logEvent(LogEvents::Start); //moved to be at the constructor(101) so that its as close to the start as we can possibly make it
    }

    void writeToDisk(const char* filePath) {
        std::ofstream logFile(filePath, std::ios::app);
        if (logFile.is_open()) {
            if (!logBuffer.empty()) {
                logBuffer.reverse();
                for (const auto& entry : logBuffer) {
                    // Concatenate seconds and nanoseconds into a single decimal number
                    logFile << entry.eventName << " "
                            << entry.time.tv_sec << "." 
                            << std::setw(9) << std::setfill('0') << entry.time.tv_nsec
                            << std::endl;
                }
            }
            logFile.close();
        } else {
            std::cerr << "Unable to open log file at " << filePath << std::endl;
        }
    }
};


#define LOG_EVENT(event) PerfLogger::getInstance().logEvent(event)

// __attribute__((constructor(101)))
// void nevafirstInitialization() {
//     LOG_EVENT(LogEvents::Start);
// }
#else


#define LOG_EVENT(event)

#endif // NEVA_TIME_BENCHMARK

#endif // PERFLOGGER_H
