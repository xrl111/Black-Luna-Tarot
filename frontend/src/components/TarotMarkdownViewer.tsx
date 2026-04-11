import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Sparkles, Moon, Sun, CheckCircle2, Star, CircleDot } from 'lucide-react';
import { cn } from '@/lib/utils';

// Helper to determine the sentiment of a text block for styling
const getSentimentIcon = (text: string) => {
  const lowerText = text.toLowerCase();
  if (lowerText.includes('ánh sáng') || lowerText.includes('tích cực') || lowerText.includes('điểm mạnh')) {
    return <Sun className="w-4 h-4 text-gold-500 mt-1 flex-shrink-0" />;
  }
  if (lowerText.includes('bóng tối') || lowerText.includes('tiêu cực') || lowerText.includes('điểm yếu')) {
    return <Moon className="w-4 h-4 text-purple-500 mt-1 flex-shrink-0" />;
  }
  if (lowerText.includes('lời khuyên')) {
    return <CheckCircle2 className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />;
  }
  return <Star className="w-4 h-4 text-mystic-400 mt-1 flex-shrink-0" />;
};

interface TarotMarkdownViewerProps {
  content: string;
  className?: string;
}

const TarotMarkdownViewer: React.FC<TarotMarkdownViewerProps> = ({ content, className }) => {
  return (
    <div className={cn("tarot-markdown-container", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // H1 and H2 - Main Section Titles
          h1: ({ node, ...props }) => (
            <h1 className="flex items-center gap-3 mt-10 mb-6 text-3xl font-cinzel font-bold text-gradient" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="flex items-center gap-2 mt-8 mb-5 text-2xl font-playfair font-bold text-mystic-700 dark:text-mystic-300 border-b border-mystic-200 dark:border-mystic-800 pb-2" {...props} />
          ),
          
          // H3 - Usually individual Cards in the reading
          h3: ({ node, children, ...props }) => {
            // Check if it's a card header (usually starts with a number or contains 'Quá khứ', etc.)
            const text = String(children);
            const isCard = text.match(/||||/) || text.includes('Quá khứ') || text.includes('Hiện tại') || text.includes('Tương lai');
            
            return (
              <div className={cn(
                "flex items-center gap-2 mt-8 mb-4",
                isCard && "bg-gradient-to-r from-mystic-50 to-transparent dark:from-mystic-900/40 p-3 rounded-lg border-l-4 border-gold-500 shadow-sm"
              )}>
                {isCard && <Sparkles className="text-gold-500 w-5 h-5 animate-pulse" />}
                <h3 className="font-playfair text-xl font-bold text-mystic-800 dark:text-mystic-200" {...props}>
                  {children}
                </h3>
              </div>
            );
          },

          // Bold text - highlight for better scannability
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-gold-700 dark:text-gold-400" {...props} />
          ),

          // Blockquotes - Mystical callouts
          blockquote: ({ node, ...props }) => (
            <blockquote 
              className="border-l-4 border-mystic-500 bg-mystic-50/50 dark:bg-mystic-900/20 px-5 py-3 my-6 italic font-cormorant text-lg rounded-r-xl shadow-sm text-mystic-800 dark:text-mystic-200 relative overflow-hidden" 
              {...props} 
            >
              {/* Decorative mystical element inside blockquote */}
              <div className="absolute top-0 right-0 opacity-5 dark:opacity-10 translate-x-1/4 -translate-y-1/4">
                <Moon className="w-24 h-24" />
              </div>
              <div className="relative z-10">{props.children}</div>
            </blockquote>
          ),

          // Lists & Items - Adding specialized bullet icons based on content
          ul: ({ node, ...props }) => (
            <ul className="space-y-3 my-4 ml-2" {...props} />
          ),
          li: ({ node, children, ...props }) => {
            // Attempt to determine the sentiment of this list item to assign an icon
            const textContent = extractTextFromNode(children);
            const Icon = getSentimentIcon(textContent);
            
            return (
              <li className="flex gap-3 items-start" {...props}>
                {Icon}
                <div className="flex-1 opacity-90 leading-relaxed font-nunito">{children}</div>
              </li>
            );
          },
          
          // Paragraphs
          p: ({ node, ...props }) => (
            <p className="my-4 leading-relaxed font-nunito text-foreground/90" {...props} />
          ),
          
          // Horizontal Rules
           hr: ({ node, ...props }) => (
             <hr className="my-8 border-t border-mystic-200 dark:border-mystic-800/50" {...props} />
           )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

// Helper function to extract plain text from React node children
function extractTextFromNode(node: React.ReactNode): string {
  if (typeof node === 'string') return node;
  if (typeof node === 'number') return String(node);
  if (Array.isArray(node)) return node.map(extractTextFromNode).join('');
  if (React.isValidElement(node) && node.props.children) {
    return extractTextFromNode(node.props.children);
  }
  return '';
}

export default TarotMarkdownViewer;
