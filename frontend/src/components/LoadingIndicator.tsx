interface LoadingIndicatorProps {
  text?: string;
}

export function LoadingIndicator({ text = "Processing..." }: LoadingIndicatorProps) {
  return (
    <div className="loading-indicator">
      <span className="spinner" aria-hidden />
      <span>{text}</span>
    </div>
  );
}

