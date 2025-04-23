"use client";

import { WebSocketProvider as WSProvider } from "@/contexts/WebSocketContext";
import React from "react";

// WebSocket URL from environment
const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || "ws://localhost:8000/ws";

export function WebSocketProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <WSProvider url={WEBSOCKET_URL}>
      {children}
    </WSProvider>
  );
} 