import KanbanBoard from "@/components/layout/KanbanBoard";

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10 border-b border-white/10 pb-6">
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            OSIRIS
          </h1>
          <p className="text-muted-foreground mt-2">
            Omni-Channel Dev Orchestrator
          </p>
        </header>

        <KanbanBoard />
      </div>
    </main>
  );
}
