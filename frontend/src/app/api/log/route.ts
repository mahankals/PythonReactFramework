/**
 * API endpoint for client-side logging.
 * Receives log entries from the browser and writes them to log files.
 */

import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const LOG_DIR = process.env.LOG_DIR || "logs";

// Ensure logs directory exists
const ensureLogDir = (): string => {
  const logPath = path.resolve(process.cwd(), LOG_DIR);
  if (!fs.existsSync(logPath)) {
    fs.mkdirSync(logPath, { recursive: true });
  }
  return logPath;
};

// Get date string for filename
const getDateString = (): string => {
  return new Date().toISOString().split("T")[0]; // YYYY-MM-DD
};

// Format log entry
const formatLogEntry = (data: {
  level: string;
  message: string;
  timestamp: string;
  url?: string;
  userAgent?: string;
  meta?: Record<string, unknown>;
}): string => {
  const entry = {
    timestamp: data.timestamp,
    level: data.level.toUpperCase(),
    message: data.message,
    source: "client",
    url: data.url,
    userAgent: data.userAgent,
    ...data.meta,
  };
  return JSON.stringify(entry) + "\n";
};

// Append to log file
const appendToLog = (filename: string, content: string): void => {
  const logPath = ensureLogDir();
  const filePath = path.join(logPath, filename);
  fs.appendFileSync(filePath, content, "utf-8");
};

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();

    const { level, message, timestamp, url, userAgent, meta } = data;

    if (!level || !message) {
      return NextResponse.json(
        { error: "Missing required fields: level, message" },
        { status: 400 }
      );
    }

    const logEntry = formatLogEntry({
      level,
      message,
      timestamp: timestamp || new Date().toISOString(),
      url,
      userAgent,
      meta,
    });

    const dateStr = getDateString();

    // Always write to app log
    appendToLog(`app-${dateStr}.log`, logEntry);

    // Write errors to error log
    if (level.toLowerCase() === "error") {
      appendToLog(`error-${dateStr}.log`, logEntry);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to write log:", error);
    return NextResponse.json(
      { error: "Failed to write log" },
      { status: 500 }
    );
  }
}
