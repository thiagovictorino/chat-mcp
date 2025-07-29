import React, { useEffect, useRef, useState } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import { Message } from '../types';
import './RichMessageItem.css';

interface Props {
  message: Message;
}

// Configure marked options
marked.setOptions({
  gfm: true,
  breaks: true,
  pedantic: false
});

// Custom renderer for better formatting
const renderer = new marked.Renderer();

// Enhanced link rendering
renderer.link = (options: any) => {
  const { href, title, tokens } = options;
  const text = tokens?.[0]?.text || '';
  const isExternal = href?.startsWith('http');
  return `<a href="${href}" ${title ? `title="${title}"` : ''} 
    class="rich-link" 
    ${isExternal ? 'target="_blank" rel="noopener noreferrer"' : ''}>
    ${text}${isExternal ? ' 🔗' : ''}
  </a>`;
};

// Enhanced code blocks with copy button
renderer.code = (options: any) => {
  const { text: code, lang: language } = options;
  const validLang = language && hljs.getLanguage(language) ? language : 'plaintext';
  let highlighted;
  
  try {
    if (language && hljs.getLanguage(language)) {
      highlighted = hljs.highlight(code, { language: validLang }).value;
    } else {
      highlighted = hljs.highlightAuto(code).value;
    }
  } catch (err) {
    highlighted = code; // Fallback to plain text
  }
  
  const codeId = `code-${Math.random().toString(36).substr(2, 9)}`;
  
  return `
    <div class="rich-code-block">
      <div class="code-header">
        <span class="code-language">${validLang}</span>
        <button class="copy-btn" data-code="${encodeURIComponent(code)}" data-id="${codeId}">
          <span class="copy-text">Copy</span>
        </button>
      </div>
      <pre><code class="hljs language-${validLang}">${highlighted}</code></pre>
    </div>
  `;
};

// Task list support
renderer.listitem = (options: any) => {
  const { text } = options;
  const isTaskList = text.includes('type="checkbox"');
  return `<li${isTaskList ? ' class="task-item"' : ''}>${text}</li>`;
};

// Better blockquotes
renderer.blockquote = (quote) => {
  return `<blockquote class="rich-quote">${quote}</blockquote>`;
};

// Tables with better styling
renderer.table = (options: any) => {
  const { header, rows } = options;
  return `
    <div class="table-wrapper">
      <table class="rich-table">
        ${header}
        ${rows}
      </table>
    </div>
  `;
};

marked.use({ renderer });

const RichMessageItem: React.FC<Props> = ({ message }) => {
  const messageRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    // Show relative time for recent messages
    if (diff < 60000) return 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    
    return date.toLocaleTimeString();
  };

  // Process content for mentions and emojis
  const processContent = (content: string) => {
    // Handle mentions
    let processed = content.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
    
    // Add emoji support
    processed = processed
      .replace(/:\)/g, '😊')
      .replace(/:\(/g, '😔')
      .replace(/:D/g, '😃')
      .replace(/:P/g, '😛')
      .replace(/:\|/g, '😐')
      .replace(/<3/g, '❤️')
      .replace(/:\+1:/g, '👍')
      .replace(/:-1:/g, '👎');
    
    return processed;
  };

  useEffect(() => {
    // Add click handlers for copy buttons
    const copyButtons = messageRef.current?.querySelectorAll('.copy-btn');
    
    const handleCopy = async (e: Event) => {
      const button = e.currentTarget as HTMLButtonElement;
      const code = decodeURIComponent(button.dataset.code || '');
      const id = button.dataset.id || '';
      
      try {
        await navigator.clipboard.writeText(code);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    };

    copyButtons?.forEach(btn => {
      btn.addEventListener('click', handleCopy);
    });

    return () => {
      copyButtons?.forEach(btn => {
        btn.removeEventListener('click', handleCopy);
      });
    };
  }, [message.content]);

  // Render markdown and sanitize
  const renderContent = () => {
    const processed = processContent(message.content);
    const html = marked(processed) as string;
    const sanitized = DOMPurify.sanitize(html, {
      ADD_ATTR: ['target', 'rel', 'data-code', 'data-id'],
      ADD_TAGS: ['button'],
    });
    
    return { __html: sanitized };
  };

  return (
    <div className="rich-message-item" ref={messageRef}>
      <div className="message-header">
        <div className="sender-info">
          <div className="sender-avatar">
            {message.sender.username.charAt(0).toUpperCase()}
          </div>
          <span className="sender-name">@{message.sender.username}</span>
          <span className="sender-role">Agent</span>
        </div>
        <span className="timestamp" title={new Date(message.timestamp).toLocaleString()}>
          {formatTimestamp(message.timestamp)}
        </span>
      </div>
      
      <div className="rich-content" dangerouslySetInnerHTML={renderContent()} />
      
      {message.read_by.length > 0 && (
        <div className="read-status">
          <span className="read-indicator" title={
            message.read_by.map(r => `@${r.username}`).join(', ')
          }>
            ✓✓ Read by {message.read_by.length}
          </span>
        </div>
      )}
      
      {/* Update copy button text dynamically */}
      <style>{`
        .copy-btn[data-id="${copiedId}"] .copy-text::after {
          content: "✓ Copied!";
        }
        .copy-btn[data-id="${copiedId}"] .copy-text {
          color: #10b981;
        }
      `}</style>
    </div>
  );
};

export default RichMessageItem;