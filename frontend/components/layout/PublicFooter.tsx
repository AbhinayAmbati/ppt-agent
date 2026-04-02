export function PublicFooter() {
  return (
    <footer className="py-8 text-center text-sm text-muted-foreground/60 border-t border-border/40 mt-auto bg-background/50 backdrop-blur-md relative z-10 w-full">
      <div className="max-w-7xl mx-auto px-8 flex justify-between items-center">
         <span>&copy; {new Date().getFullYear()} Auto-PPT.</span>
         <span className="font-serif italic">Agentic flow</span>
      </div>
    </footer>
  );
}
