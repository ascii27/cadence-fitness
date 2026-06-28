import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ExerciseDetail from "../src/components/ExerciseDetail";
import ExerciseList from "../src/components/ExerciseList";
import type { CatalogExercise, Exercise } from "../src/lib/types";

const pushup: CatalogExercise = {
  slug: "push-up",
  name: "Push-up",
  category: "push",
  target: ["chest", "triceps"],
  difficulty: "intermediate",
  low_impact: true,
  equipment: "none",
  unit: "reps",
  instructions: ["Start in a high plank.", "Lower the chest.", "Press back up."],
  cues: ["Brace the core", "Neck long"],
  image: "/exercises/push-up.svg",
};

describe("ExerciseDetail", () => {
  it("renders instructions, cues, and badges", () => {
    render(<ExerciseDetail exercise={pushup} onClose={() => {}} />);
    expect(screen.getByRole("heading", { name: "Push-up" })).toBeInTheDocument();
    expect(screen.getByText("Start in a high plank.")).toBeInTheDocument();
    expect(screen.getByText("Brace the core")).toBeInTheDocument();
    expect(screen.getByText("Low impact")).toBeInTheDocument();
    expect(screen.getByText("No equipment")).toBeInTheDocument();
  });

  it("renders nothing when no exercise is selected", () => {
    const { container } = render(<ExerciseDetail exercise={null} onClose={() => {}} />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe("ExerciseList", () => {
  function renderWithCatalog(exercises: Exercise[]) {
    const qc = new QueryClient();
    qc.setQueryData(["exercises"], [pushup]);
    return render(
      <QueryClientProvider client={qc}>
        <ExerciseList exercises={exercises} />
      </QueryClientProvider>,
    );
  }

  it("opens the detail drawer for a catalog-linked exercise", async () => {
    renderWithCatalog([{ name: "Push-ups", reps: null, note: "max reps", slug: "push-up" }]);
    expect(screen.getByText("Push-ups")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /how-to/i }));
    // Drawer now shows the catalog instructions.
    expect(screen.getByText("Lower the chest.")).toBeInTheDocument();
  });

  it("renders an unlinked exercise without a how-to button", () => {
    renderWithCatalog([{ name: "Mystery move", reps: null, note: null, slug: null }]);
    expect(screen.getByText("Mystery move")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /how-to/i })).not.toBeInTheDocument();
  });
});
