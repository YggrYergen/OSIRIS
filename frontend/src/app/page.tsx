import KanbanBoard from "@/components/layout/KanbanBoard";
import NavigationHeader from "@/components/layout/NavigationHeader";

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-7xl mx-auto">
        <NavigationHeader />
        <KanbanBoard />
      </div>
    </main>
  );
}
