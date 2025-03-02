import React, { useRef, useState, useCallback } from 'react';

interface IframeEmailViewerProps {
  htmlContent: string;
}

/**
 * IframeEmailViewer loads HTML into an iframe and auto-resizes
 * the iframe's height to match the content to avoid double scrollbars.
 */
export function IframeEmailViewer({ htmlContent }: IframeEmailViewerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [iframeHeight, setIframeHeight] = useState<number>(600);

  /**
   * Called when the iframe loads. Measures the content height and updates state.
   */
  const handleIframeLoad = useCallback(() => {
    if (!iframeRef.current) return;

    const iframe = iframeRef.current;
    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
    if (!iframeDoc) return;

    // Use scrollHeight to get the total height of the iframe content.
    const newHeight = iframeDoc.body.scrollHeight;
    setIframeHeight(newHeight);
  }, []);

  return (
    <iframe
      ref={iframeRef}
      srcDoc={htmlContent}
      onLoad={handleIframeLoad}
      sandbox="allow-same-origin allow-popups allow-scripts"
      style={{
        width: '100%',
        border: 'none',
        // Dynamically set the height
        height: `${iframeHeight}px`,
        // Optional: smooth scrolling inside the iframe
        overflow: 'auto'
      }}
    />
  );
}

export default IframeEmailViewer;
