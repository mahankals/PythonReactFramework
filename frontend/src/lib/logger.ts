/**
 * Application logging with daily rotation and auto-cleanup.
 *
 * Log files (server-side only):
 * - logs/app-YYYY-MM-DD.log: All logs (INFO, DEBUG, WARNING, ERROR)
 * - logs/error-YYYY-MM-DD.log: Error logs only
 *
 * Client-side: Logs are sent to /api/log endpoint
 */

import pino from "pino";
import fs from "fs";
import path from "path";
import { createStream } from "rotating-file-stream";

// Configuration
const LOG_DIR = process.env.LOG_DIR || "logs";
const LOG_RETENTION_DAYS = parseInt(process.env.LOG_RETENTION_DAYS || "30", 10);
const LOG_LEVEL = process.env.LOG_LEVEL || "info";
const NODE_ENV = process.env.NODE_ENV || "development";

// Date formatter for filenames
const getDateString = (): string => {
  const now = new Date();
  return now.toISOString().split("T")[0]; // YYYY-MM-DD
};

// Ensure logs directory exists (server-side only)
const ensureLogDir = (): void => {
  if (typeof window === "undefined") {
    const logPath = path.resolve(process.cwd(), LOG_DIR);
    if (!fs.existsSync(logPath)) {
      fs.mkdirSync(logPath, { recursive: true });
    }
  }
};

// Clean up old log files
const cleanupOldLogs = (): void => {
  if (typeof window !== "undefined") return;

  const logPath = path.resolve(process.cwd(), LOG_DIR);
  if (!fs.existsSync(logPath)) return;

  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - LOG_RETENTION_DAYS);

  const files = fs.readdirSync(logPath);
  for (const file of files) {
    // Match app-YYYY-MM-DD.log or error-YYYY-MM-DD.log
    const match = file.match(/^(app|error)-(\d{4}-\d{2}-\d{2})\.log$/);
    if (match) {
      const fileDate = new Date(match[2]);
      if (fileDate < cutoffDate) {
        fs.unlinkSync(path.join(logPath, file));
      }
    }
  }
};

// Create rotating file stream for logs
const createLogStream = (prefix: string) => {
  ensureLogDir();

  return createStream(
    (time: Date | number, index?: number) => {
      const date = time instanceof Date ? time : new Date();
      return `${prefix}-${date.toISOString().split("T")[0]}.log`;
    },
    {
      path: path.resolve(process.cwd(), LOG_DIR),
      interval: "1d", // Rotate daily
      maxFiles: LOG_RETENTION_DAYS,
    }
  );
};

// Server-side logger with file rotation
const createServerLogger = () => {
  ensureLogDir();
  cleanupOldLogs();

  const streams: pino.StreamEntry[] = [];

  // Console output
  if (NODE_ENV === "development") {
    streams.push({
      level: "debug",
      stream: process.stdout,
    });
  }

  // App log file (all levels)
  streams.push({
    level: LOG_LEVEL as pino.Level,
    stream: createLogStream("app"),
  });

  // Error log file (errors only)
  streams.push({
    level: "error",
    stream: createLogStream("error"),
  });

  return pino(
    {
      level: LOG_LEVEL,
      timestamp: pino.stdTimeFunctions.isoTime,
      formatters: {
        level: (label) => ({ level: label.toUpperCase() }),
      },
    },
    pino.multistream(streams)
  );
};

// Client-side logger (sends to API)
const createClientLogger = () => {
  const sendLog = async (
    level: string,
    message: string,
    meta?: Record<string, unknown>
  ) => {
    try {
      await fetch("/api/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          level,
          message,
          meta,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          userAgent: navigator.userAgent,
        }),
      });
    } catch {
      // Fallback to console if API fails
      console.error("Failed to send log to server");
    }
  };

  return {
    debug: (message: string, meta?: Record<string, unknown>) =>
      console.debug(message, meta),
    info: (message: string, meta?: Record<string, unknown>) =>
      console.info(message, meta),
    warn: (message: string, meta?: Record<string, unknown>) => {
      console.warn(message, meta);
      sendLog("warn", message, meta);
    },
    error: (message: string, meta?: Record<string, unknown>) => {
      console.error(message, meta);
      sendLog("error", message, meta);
    },
  };
};

// Export appropriate logger based on environment
export const logger =
  typeof window === "undefined" ? createServerLogger() : createClientLogger();

// Type-safe logging functions for both environments
export const log = {
  debug: (message: string, meta?: Record<string, unknown>) => {
    if (typeof window === "undefined") {
      (logger as pino.Logger).debug(meta || {}, message);
    } else {
      (logger as ReturnType<typeof createClientLogger>).debug(message, meta);
    }
  },
  info: (message: string, meta?: Record<string, unknown>) => {
    if (typeof window === "undefined") {
      (logger as pino.Logger).info(meta || {}, message);
    } else {
      (logger as ReturnType<typeof createClientLogger>).info(message, meta);
    }
  },
  warn: (message: string, meta?: Record<string, unknown>) => {
    if (typeof window === "undefined") {
      (logger as pino.Logger).warn(meta || {}, message);
    } else {
      (logger as ReturnType<typeof createClientLogger>).warn(message, meta);
    }
  },
  error: (message: string, meta?: Record<string, unknown>) => {
    if (typeof window === "undefined") {
      (logger as pino.Logger).error(meta || {}, message);
    } else {
      (logger as ReturnType<typeof createClientLogger>).error(message, meta);
    }
  },
};

export default log;
