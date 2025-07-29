import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Highlight, themes } from 'prism-react-renderer';
import { Message } from '../types';
import './EnhancedMessageItem.css';

interface Props {
  message: Message;
}

const EnhancedMessageItem: React.FC<Props> = ({ message }) => {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="enhanced-message-item">
      <div className="message-header">
        <span className="sender">@{message.sender.username}</span>
        <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
      </div>
      
      <div className="message-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({node, className, children, ...props}: any) {
              const match = /language-(\w+)/.exec(className || '');
              const codeString = String(children).replace(/\n$/, '');
              const codeId = `${message.message_id}-${Math.random()}`;
              
              const inline = node?.position?.start.line === node?.position?.end.line;
              return !inline && match ? (
                <div className="code-block-wrapper">
                  <div className="code-block-header">
                    <span className="code-language">{match[1]}</span>
                    <button
                      className="copy-button"
                      onClick={() => copyToClipboard(codeString, codeId)}
                    >
                      {copiedCode === codeId ? '✓ Copied' : 'Copy'}
                    </button>
                  </div>
                  <Highlight
                    theme={themes.github}
                    code={codeString}
                    language={match[1]}
                  >
                    {({ className, style, tokens, getLineProps, getTokenProps }) => (
                      <pre className={className} style={{...style, margin: 0, borderRadius: '0 0 8px 8px'}}>
                        {tokens.map((line, i) => (
                          <div key={i} {...getLineProps({ line })}>
                            {line.map((token, key) => (
                              <span key={key} {...getTokenProps({ token })} />
                            ))}
                          </div>
                        ))}
                      </pre>
                    )}
                  </Highlight>
                </div>
              ) : (
                <code className={`inline-code ${className}`} {...props}>
                  {children}
                </code>
              )
            },
            p: ({children}) => {
              const processChildren = (child: any): any => {
                if (typeof child === 'string') {
                  const mentionRegex = /@(\w+)/g;
                  const parts = child.split(mentionRegex);
                  return parts.map((part, index) => {
                    if (index % 2 === 1) {
                      return <span key={index} className="mention">@{part}</span>;
                    }
                    return part;
                  });
                }
                return child;
              };
              
              return (
                <p>
                  {React.Children.map(children, processChildren)}
                </p>
              );
            },
            h1: ({children}) => <h1 className="message-h1">{children}</h1>,
            h2: ({children}) => <h2 className="message-h2">{children}</h2>,
            h3: ({children}) => <h3 className="message-h3">{children}</h3>,
            strong: ({children}) => <strong className="message-bold">{children}</strong>,
            em: ({children}) => <em className="message-italic">{children}</em>,
            ul: ({children}) => <ul className="message-list">{children}</ul>,
            ol: ({children}) => <ol className="message-list ordered">{children}</ol>,
            li: ({children}) => <li className="message-list-item">{children}</li>,
            blockquote: ({children}) => <blockquote className="message-quote">{children}</blockquote>,
            a: ({href, children}) => (
              <a href={href} className="message-link" target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
            table: ({children}) => (
              <div className="table-wrapper">
                <table>{children}</table>
              </div>
            ),
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
      
      {message.read_by.length > 0 && (
        <div className="read-receipts">
          <span className="read-indicator" title={
            message.read_by.map(r => `@${r.username}`).join(', ')
          }>
            ✓✓ {message.read_by.length}
          </span>
        </div>
      )}
    </div>
  );
};

export default EnhancedMessageItem;