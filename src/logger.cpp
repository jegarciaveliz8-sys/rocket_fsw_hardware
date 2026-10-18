#include <SD.h>
#include <SPI.h>
#include "logger.h"
#include "config.h"

File flightFile;
bool sdInitialized = false;

bool initLogger() {
    if (!SD.begin(SD_CS_PIN)) {
        return false;
    }
    
    flightFile = SD.open("flight_log.csv", FILE_WRITE);
    if (flightFile) {
        flightFile.println("Timestamp_ms,State,Ax,Ay,Az,Altitude_m");
        flightFile.flush();
        sdInitialized = true;
        return true;
    }
    return false;
}

void logData(const String &data) {
    if (sdInitialized && flightFile) {
        flightFile.println(data);
        flightFile.flush(); 
    }
}
