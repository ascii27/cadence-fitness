import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import ReadinessCheck from "../src/components/ReadinessCheck";
import SessionCard from "../src/components/SessionCard";
import StarRating from "../src/components/StarRating";
import DayNav from "../src/components/DayNav";
import { isoAddDays, todayISO } from "../src/lib/format";
import type { DerivedSession } from "../src/lib/types";

const baseSession: DerivedSession = {
  day_of_week: "monday",
  session_type: "strength",
  label: "Upper Body & Core",
  modality: "amrap",
  duration_minutes: 15,
  exercises: [{ name: "Push-ups", reps: null, note: "max reps" }],
  hr_zone: null,
  hr_cap_bpm: null,
  progression_rule: null,
  is_rest: false,
  swapped: false,
  swap_reason: null,
  routine_version: 1,
};

describe("ReadinessCheck", () => {
  it("reports the chosen answer", async () => {
    const onAnswer = vi.fn();
    render(<ReadinessCheck onAnswer={onAnswer} />);
    await userEvent.click(screen.getByText("Joint pain"));
    expect(onAnswer).toHaveBeenCalledWith("joint_pain");
  });
});

describe("SessionCard", () => {
  it("renders the session and a Log CTA when not logged", () => {
    render(
      <MemoryRouter>
        <SessionCard session={baseSession} log={null} dateLabel="Monday" />
      </MemoryRouter>,
    );
    expect(screen.getByText("Upper Body & Core")).toBeInTheDocument();
    expect(screen.getByText("Push-ups")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /log workout/i })).toBeInTheDocument();
  });

  it("shows the mobility swap notice when swapped", () => {
    const swapped: DerivedSession = {
      ...baseSession,
      session_type: "mobility",
      label: "Mobility & Stretch",
      swapped: true,
      swap_reason: "joint_pain",
    };
    render(
      <MemoryRouter>
        <SessionCard session={swapped} log={null} dateLabel="Monday" />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Swapped to mobility/i)).toBeInTheDocument();
  });
});

describe("StarRating", () => {
  it("selects a rating on tap", async () => {
    const onChange = vi.fn();
    render(<StarRating value={null} onChange={onChange} />);
    await userEvent.click(screen.getByLabelText("4 stars"));
    expect(onChange).toHaveBeenCalledWith(4);
  });
});

describe("SessionCard relativity", () => {
  it("shows an upcoming preview (no log CTA) for future days", () => {
    render(
      <MemoryRouter>
        <SessionCard session={baseSession} log={null} dateLabel="Monday" relativity="future" />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Upcoming/i)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /log/i })).not.toBeInTheDocument();
  });

  it("offers 'Log this day' for past days", () => {
    render(
      <MemoryRouter>
        <SessionCard session={baseSession} log={null} dateLabel="Monday" relativity="past" logHref="/log?date=2026-06-01" />
      </MemoryRouter>,
    );
    expect(screen.getByRole("link", { name: /log this day/i })).toBeInTheDocument();
  });
});

describe("DayNav", () => {
  it("steps to the next and previous day", async () => {
    const onChange = vi.fn();
    const today = todayISO();
    render(<DayNav dateIso={today} onChange={onChange} />);
    await userEvent.click(screen.getByLabelText("Next day"));
    expect(onChange).toHaveBeenCalledWith(isoAddDays(today, 1));
    await userEvent.click(screen.getByLabelText("Previous day"));
    expect(onChange).toHaveBeenCalledWith(isoAddDays(today, -1));
  });

  it("labels the current day 'Today'", () => {
    render(<DayNav dateIso={todayISO()} onChange={() => {}} />);
    expect(screen.getByText("Today")).toBeInTheDocument();
  });
});
