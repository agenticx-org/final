"use client";

import { useWebSocket, useWebSocketHandlers } from "@/contexts/WebSocketContext";
import { useChatStore } from "@/store/chat-store";
import { MessageContent } from "@/types/chat";
import { Plus } from "@phosphor-icons/react";
import { useEffect } from "react";
import { Button } from "../ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";

export function Chat() {
  const {
    message,
    isLoading,
    isStreaming,
    streamingContent,
    selectedModel,
    messages,
    isAgent,
    setMessage,
    setSelectedModel,
    setIsLoading,
    setIsStreaming,
    updateStreamingContent,
    commitStreamingContent,
    clearStreamingContent,
    addUserMessage,
    handleFileChange,
    setIsAgent,
    clearMessages,
    clearSelectedTexts,
    addAgentResponse,
  } = useChatStore();

  // Get WebSocket from context
  const { isConnected, sendMessage } = useWebSocket();

  // Register message handlers
  useWebSocketHandlers({
    onStatusChange: (status) => {
      if (status === 'thinking') {
        setIsLoading(true);
        setIsStreaming(false);
      } else if (status === 'complete') {
        setIsLoading(false);
        setIsStreaming(false);
        commitStreamingContent();
      } else if (status === 'error') {
        setIsLoading(false);
        setIsStreaming(false);
        clearStreamingContent();
      }
    },
    onChunk: (content: MessageContent) => {
      if (!isStreaming) {
        setIsStreaming(true);
      }
      updateStreamingContent(content);
    },
    onMessage: (data: any) => {
      console.log("Received full message:", data);
      // Check if the message has the expected structure
      if (
        data &&
        typeof data === 'object' &&
        typeof data.type === 'string' &&
        typeof data.content === 'string' &&
        typeof data.content_type === 'string' &&
        ['plan', 'findings', 'done'].includes(data.type)
      ) {
        // Format based on content_type
        const formattedContent: MessageContent = data.content_type === 'md'
          ? { type: 'markdown', text: data.content }
          : { type: 'text', text: data.content };
        
        // Add the formatted content as a new agent message
        addAgentResponse([formattedContent]);

      } else {
        // Handle other potential message formats or log a warning
        console.warn("Received message format is not the expected plan/findings/done structure:", data);
        // You might want to add fallback logic here if other message types are expected
        // For example, handling simple text messages:
        // if (typeof data === 'string') {
        //   addAgentResponse([{ type: 'text', text: data }]);
        // } else if (data && data.text && typeof data.text === 'string') {
        //   addAgentResponse([{ type: 'text', text: data.text }]);
        // }
      }
    },
  });

  // Custom handle submit
  const handleSubmit = () => {
    if (!message.trim() || !isConnected) return;

    // Add user message to the chat
    addUserMessage(message);
    
    // Send the message via WebSocket
    sendMessage(message);
    
    // Clear the input
    setMessage("");
    clearSelectedTexts();
  };

  const handleClearChat = () => {
    clearMessages();
    clearSelectedTexts();
  };

  // Show connection status
  useEffect(() => {
    if (!isConnected) {
      console.warn("WebSocket disconnected");
    }
  }, [isConnected]);

  return (
    <>
      <div className="flex-grow flex-shrink-0 h-[51px] w-full bg-white z-[2]"></div>
      <div className="flex flex-col h-[calc(100vh-51px)]">
        <div className="border-b border-b-default-200 flex items-center justify-between bg-white gap-x-3 px-3 h-[46px] font-medium">
          <div className="flex items-center gap-2">
            Agent
            {!isConnected && (
              <span className="text-xs text-red-500 font-normal">
                (WebSocket disconnected)
              </span>
            )}
          </div>
          <div>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={handleClearChat}>
                  <Plus className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="left">
                <p className="text-xs">New Chat</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
        <div className="flex-1 relative overflow-y-auto scrollbar-custom overflow-x-hidden">
          <MessageList 
            messages={messages} 
            isAgent={isAgent} 
            streamingContent={isStreaming ? streamingContent : undefined}
          />
        </div>
        <ChatInput
          message={message}
          isLoading={isLoading || isStreaming}
          selectedModel={selectedModel}
          onMessageChange={setMessage}
          onModelChange={setSelectedModel}
          onSubmit={handleSubmit}
          onFileChange={handleFileChange}
          onModeChange={setIsAgent}
        />
      </div>
    </>
  );
}

export default Chat;
